from dodocker.parser import TaskGroup, DodockerParseError
from dodocker import run_dodocker_cli
import os, pytest

class TestTemplates:
    def test_template(self, tmpdir_copy, docker_helper):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        assert tmpdir_copy.join(
            'image1/scratch.txt').read() == docker_helper.get_file_contents_from_image(
                'dodockertest/template-test-scratch','output.txt').decode('utf8')
        assert tmpdir_copy.join(
            'image1/busybox.txt').read() == docker_helper.get_file_contents_from_image(
                'dodockertest/template-test-busybox','output.txt').decode('utf8')

        assert docker_helper.get_file_contents_from_image(
            'dodockertest/template-test-busybox',
            'someotherfile.txt').decode('utf8') == 'This is some otherfile in the busybox'

        assert docker_helper.get_file_contents_from_image(
            'dodockertest/template-test-scratch',
            'someotherfile.txt').decode('utf8') == 'This is some otherfile in the scratch'
                
