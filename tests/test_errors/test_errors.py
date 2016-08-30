from dodocker import run_dodocker_cli
import os, pytest, requests

class TestErrors:
    def test_bad_dockerfile(self, tmpdir_copy):
        with tmpdir_copy.as_cwd():
            try:
                run_dodocker_cli(['-o','output.txt','build'])
            except SystemExit:
                pass
        output = tmpdir_copy.join('output.txt').read()
        assert 'Unknown instruction: RN' in output
