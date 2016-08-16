from dodocker import run_dodocker_cli
import os, pytest

class TestShellBuild:
    def test_build(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('.  build_dodockertest/shtest1',
                                    '.  build_dodockertest/shtest2',
                                    ''))

    def test_2nd_build(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('-- build_dodockertest/shtest1',
                                    '-- build_dodockertest/shtest2',
                                    ''))

    def test_3d_build_with_touch(self, tmpdir_copy):
        tmpdir_copy.join('image1','test.sh').open('a').write('\n')
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('.  build_dodockertest/shtest1',
                                    '-- build_dodockertest/shtest2',
                                    ''))
        
