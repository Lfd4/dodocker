from dodocker import run_dodocker_cli
import os, pytest

class TestScratch:
    def test_given_build(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])


