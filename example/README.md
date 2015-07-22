Create an environment for building your own base images
=======================================================

1. Have docker installed.
2. Install sudo, python-virtualenv
3. Install a recent debootstrap. For debian wheezy you need to `sudo apt-get install -t wheezy-backports debootstrap`
2. Create a user for building images. Add this user to /etc/group and to sudoers
3. Login to your build user.
4. execute `virtualenv build_dir`
5. `cd build_dir`
6. Activate the virtualenv with `. bin/activate`
7. git clone dodocker
8. `pip install dodocker`
9. `cd dodocker/example`
10. `dodocker`

Dodocker will now build debian:wheezy debian:jessie and ubuntu:14.04. In images/baseimages you
will find the Dockerfiles to customize the base images. Even better add your new images
depending on a base image.

