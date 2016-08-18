Create an dodocker environment from scratch
===========================================

This readme describes the steps to install a dodocker build environment from scratch. This method will install
dodocker into a virtualenv. It is not run inside a docker container. In this way the host docker client is used.

Prerequisites
-------------

1. Have docker installed.
2. Install sudo, python-virtualenv, git
3. For building base images you may need to install some bootstrap script or whatever. For building debian base images you would need to install debootstrap. Should your build host be running debian wheezy you need to `sudo apt-get install -t wheezy-backports debootstrap` with apt sources containing backports config.

Setup the environment
---------------------

To setup dodocker for the current (root) user follow this recipe. 

    # create a python virtualenv environment
    virtualenv build_dir
    cd build_dir
    # Activate the virtualenv 
    . bin/activate
    pip install dodocker
    
You are now ready to use dodocker. For every new login session, you have to do `. bin/activate` to
enter the build environment. As an alternative you can call bin/dodocker directly (symlinking it, andding it to
search path). 
    
Test your setup:
----------------
Type `dodocker --help`. You should now see the integrated help.

Test your setup with a build !
------------------------------
Your are already in the examples directory. Check out the dodocker.yaml file. It contains some build definitions
which are building Ubuntu, Debian, and Alpine.

Additionally registry:2 is provided as an independent build. Which is the basic idea of dodocker:
Compose your own builds.

You can build all images by `dodocker build -v`. Or you can just build one of the images like
`dodocker build -v debian:jessie`.

`-v` is running the build in verbose mode. You will see all commands issued by docker.


