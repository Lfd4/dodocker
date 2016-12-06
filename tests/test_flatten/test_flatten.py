from dodocker import run_dodocker_cli
import os, pytest

class TestScratch:
    def test_flatten_build(self,tmpdir_copy, docker_helper):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        data = docker_helper.inspect_image('dodockertest/flatten1')
        assert data['Size'] == 0
