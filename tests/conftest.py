import pytest
from distutils.dir_util import copy_tree
import os

@pytest.yield_fixture
def tmpdir_copy(tmpdir, request):
    with tmpdir.as_cwd():
        copy_tree(os.path.dirname(request.module.__file__),
                  os.getcwd())
    yield tmpdir
