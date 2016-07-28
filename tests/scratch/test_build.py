from doocker import run_dodocker_cli

def test_build(tempdir):
    run_dodocker_cli(['build'])
