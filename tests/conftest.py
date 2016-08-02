import pytest
from distutils.dir_util import copy_tree
import os, hashlib, subprocess

@pytest.yield_fixture(scope='module')
def tmpdir_copy(tmpdir_factory, request):
    tmpdir_name = hashlib.md5(str(request.node)).hexdigest()
    t = tmpdir_factory.mktemp(tmpdir_name)
    with t.as_cwd():
        copy_tree(os.path.dirname(request.module.__file__),
                  os.getcwd())
    yield t

def find_and_delete_testimages():
    images = " ".join(subprocess.check_output(
        "docker images | grep dodockertest | awk '{print $1}'", shell=True
        ).split())
    if not images:
        return
    subprocess.check_call(["docker rmi {}".format(images)], shell=True)
    
@pytest.yield_fixture(scope='session', autouse=True)
def on_session_start_end_clean_docker_from_testimages():
    find_and_delete_testimages()
    yield
    find_and_delete_testimages()
