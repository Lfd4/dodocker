from dodocker import run_dodocker_cli
import os, pytest

def test_build(tmpdir_copy):
    with tmpdir_copy.as_cwd():
        run_dodocker_cli(['build'])
