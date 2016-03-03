Create an environment for building your own base images
=======================================================

1. Have docker installed.
2. Install sudo, python-virtualenv, git
3. Install a recent debootstrap. For debian wheezy you need to `sudo apt-get install -t wheezy-backports debootstrap`

Variant A: Using the current (root) user and creating a directory with the build environment

    # create a python virtualenv environment
    virtualenv build_dir
    cd build_dir
    # Activate the virtualenv 
    . bin/activate
    pip install dodocker
    
You are now ready to use dodocker. If you start a new login session, you have to do `. bin/activate` again to
**initialize the build environment manually**.
    
Variant B: Create a new non root user dedicated to building images

    # create a 'build' user, create the homedir, use bash and add the user to group docker 
    useradd -c "docker builder" -ms /bin/bash -G docker build 
    su - build # Login to your build user.
    # create a python virtual env in the home directory
    virtualenv ~
    . ~/bin/activate
    pip install dodocker
    
Your are now ready to use dodocker. **On every login** the build envirtonment is **initialized automatically**.

Test your setup:
----------------
Type `dodocker --help`. You should now see the integrated help.

Test your setup with a build !
------------------------------
Your are already in the examples directory. Check out the dodocker.yaml file. It contains some build definitions
which are building Ubuntu 14.04, Debian Wheezy and Debian Jessie.

You can build all images by `dodocker build -v`. Or you can just build one of the images like
`dodocker build -v debian:jessie`.

`-v` is running the build in verbose mode. You will see all commands issued by docker.


