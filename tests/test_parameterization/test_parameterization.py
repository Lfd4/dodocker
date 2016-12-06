from dodocker import run_dodocker_cli
import os, pytest

class TestParamizeThreeBuilds:
    def test_dodocker_yaml(self,tmpdir_copy,docker_helper):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
            contents_v1 = docker_helper.get_file_contents_from_image(
                'dodockertest/paramtest1:v1','test.out').decode('utf8')
            assert contents_v1 == 'A one\nB two\nC three\n'
            contents_v2 = docker_helper.get_file_contents_from_image(
                'dodockertest/paramtest1:v2','test.out').decode('utf8')
            assert contents_v2 == 'A\nB no_default\nC\n'
            contents_latest = docker_helper.get_file_contents_from_image(
                'dodockertest/paramtest1:latest','test.out').decode('utf8')
            assert contents_latest == 'A eins\nB zwei\nC drei\n'
            contents_v3 = docker_helper.get_file_contents_from_image(
                'dodockertest/paramtest1:v3','test.out').decode('utf8')
            assert contents_v3 == 'A eins\nB zwei\nC drei\n'
            
            

