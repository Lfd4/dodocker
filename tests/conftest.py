import pytest
from distutils.dir_util import copy_tree
import os, hashlib, subprocess

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
def docker_registry(scope='session'):
    subprocess.check_call(
        ['docker run -d -p 5000:5000 --name dodockerregistry registry:2'],
        shell=True)
    yield None
    subprocess.check_call(
        ['docker stop dodockerregistry && docker rm dodockerregistry'],
        shell=True)
