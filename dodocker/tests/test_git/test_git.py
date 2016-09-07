from dodocker import run_dodocker_cli
import os, pytest

class TestGit:
    def test_given_build(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('.  git_dodockertest/gittest',
                                    '.  build_dodockertest/gittest',
                                    '.  build_dodockertest/a-dependent-image',
                                    ''))

    def test_2nd_build_is_cached(self,tmpdir_copy):
        with tmpdir_copy.as_cwd():
            run_dodocker_cli(['-o','output.txt','build'])
        output = tmpdir_copy.join('output.txt').open().read()
        assert output == '\n'.join(('.  git_dodockertest/gittest',
                                    '.  build_dodockertest/gittest',
                                    '-- build_dodockertest/a-dependent-image',
                                    ''))

