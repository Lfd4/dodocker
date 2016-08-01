import pytest
from distutils.dir_util import copy_tree
import os, hashlib

@pytest.yield_fixture(scope='module')
def tmpdir_copy(tmpdir_factory, request):
    tmpdir_name = hashlib.md5(str(request.node)).hexdigest()
    t = tmpdir_factory.mktemp(tmpdir_name)
    with t.as_cwd():
        copy_tree(os.path.dirname(request.module.__file__),
                  os.getcwd())
    yield t


    
@pytest.yield_fixture(scope='session', autouse=True)
def on_session_start_clean_docker():
    yield
