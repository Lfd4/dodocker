========
dodocker
========

Overview
========

dodocker is a build and registry upload tool for docker images. It is based upon 
[doit task management & automation tool](http://pydoit.org/). It reads a dodocker.yaml task
definition file and can run Dockerfiles as well as shell scripts. 

dodocker was especially conceived to build docker images from scratch without the need to
use images from docker.com registry. Nevertheless it is possible to base your builds on
the public docker registry.

Quick start
===========

The build is defined in a dodocker.yaml file. Every build is described as a list of dictionary
entries where every entry is defining a build whereas a build can be done by executing a Dockerfile
or executing a shell action.

Such a entry defines the following fields:

for shell actions:

    image: name of image
    shell_action: "command to be exected" 
    depends: image name to depend upon (optional)
    tags: [tag1,tag2,...] (optional list of tags)

for Dockerfiles:

    image: name of image
    docker_build: true (mandatory for building a Dockerfile)
    depends: image name to depend upon (optional)
    path: /path/to/directory
    file_dep: [file1, file2, dir/file3, ...] (files to watch for changes, optional)
    dockerfile: optional dockerfile
    tags: [tag1,tag2,...] (optional list of tags)

Building images
===============

Inside the directory that carries the dodocker.yaml file type:

    $ dodocker

This will call the default `build` task to be run. If a build sub-task errors out, the stdout
from this build is sent to stdout. If you like to generally see the output of your builds, it is
possible to raise verbosity which is a feature of doit.

    $ dodocker --verbosity 2

Likewise it is possible to build images in parallel. Although there seems to be a race condition
within docker to make a build fail from time to time, when running in parallel. This will run
4 build processes in parallel.

    $ dodocker -n 4

Uploading to a private registry
===============================

Before uploading docker images, the registry path has to be set.

    $ dodocker set_registry registry.yourdomain.com:443

To allow registry uploads via http or unsigned certificates it is possible to allow insecure
registries:

    $ dodocker set_insecure yes

switch it back to secure only:

    $ dodocker set_insecure no

Settings are saved in ~/.dodocker.yaml.

To upload:

    $ dodocker upload

Now you have your images inside your private registry.

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



