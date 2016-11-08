import pytest
from distutils.dir_util import copy_tree
import os, hashlib, subprocess, time, docker, tarfile
from io import BytesIO

@pytest.yield_fixture(scope='module')
def tmpdir_copy(tmpdir_factory, request):
    tmpdir_name = hashlib.md5(str(request.node).encode('utf-8')).hexdigest()
    t = tmpdir_factory.mktemp(tmpdir_name)
    with t.as_cwd():
        copy_tree(os.path.dirname(request.module.__file__),
                  os.getcwd())
    yield t

def find_and_delete_testimages():
    images = set(subprocess.check_output(
        "docker images | grep dodockertest | awk '{print $3}'", shell=True).split())
    if not images:
        return
    done = set()
    for mode in ('','-f'):
        for i in images:
            try:
                subprocess.check_call(["docker rmi {} {}".format(mode,i)], shell=True)
            except subprocess.CalledProcessError:
                continue
            done.add(i)
        images = images - done
            
    
@pytest.yield_fixture(scope='session', autouse=True)
def on_session_start_end_clean_docker_from_testimages():
    find_and_delete_testimages()
    yield
    find_and_delete_testimages()
    
@pytest.yield_fixture(scope='session')
def docker_registry():
    subprocess.check_call(
        ['docker run -d -p 5000:5000 --name dodockerregistry registry:2'],
        shell=True)
    time.sleep(1) # wait for registry to become really ready
    yield None
    subprocess.check_call(
        ['docker stop dodockerregistry && docker rm dodockerregistry'],
        shell=True)

@pytest.yield_fixture(scope='session')
def docker_helper():
    yield DockerHelper()
    
class DockerHelper:
    def __init__(self):
        self.dc = docker.Client(version='auto')
    def get_file_contents_from_image(self, image, path):
        container = self.dc.create_container(image, '/bin/true')
        tar_stream, stat = self.dc.get_archive(container, path)
        with tarfile.TarFile(fileobj=BytesIO(tar_stream.read())) as tf:
            data = tf.extractfile(path)
        self.dc.remove_container(container)
        return data.read()
