from dodocker import run_dodocker_cli
import os, pytest

class TestScratch:
    def test_given_build(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('.  build_dodockertest/test1',
                                    '.  build_dodockertest/test2',
                                    '.  build_dodockertest/test3',
                                    ''))

    def test_2nd_build_is_cached(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('-- build_dodockertest/test1',
                                    '-- build_dodockertest/test2',
                                    '-- build_dodockertest/test3',
                                    ''))

    def test_dependency_rules_by_adding_stuff(self,tmpdir_copy):
        tmpdir_copy.join('image2','Dockerfile').open('a').write('ADD b.txt /b2.txt\n')
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('-- build_dodockertest/test1',
                                    '.  build_dodockertest/test2',
                                    '.  build_dodockertest/test3',
                                    ''))

