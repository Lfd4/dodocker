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
    pull: force a pull for dependant [remote] image (optional, default is false. available when docker_build is true)
    tags: [tag1,tag2,...] (optional list of tags)

Building images
===============

Inside the directory that carries the dodocker.yaml file type:

    $ dodocker

This will call the default `build` task to be run. If a build sub-task errors out, the stdout
from this build is sent to stdout. If you like to generally see the output of your builds, it is
possible to get this verbosity by using the flag provided by doit.

    $ dodocker --verbosity 2

Likewise it is possible to build images in parallel. A warning though: There seems to be a race
condition within docker to make a build fail from time to time, when running in parallel.
Restarting the build will finish the build eventually.
This will run 4 build processes in parallel:

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

Please consulte the README.md file in the example directory. This is a complete setup and starting
point for building your own Debian and Ubuntu base images. It is based on the mkimage tool
courtesy of the docker project.



