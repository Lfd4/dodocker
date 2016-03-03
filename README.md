========
dodocker
========

Overview
========

dodocker is a dependency based build tool for docker images. It supports uploading 
built images to a private registry. It is based upon [doit task management & automation tool](http://pydoit.org/). 
The build configuration is provided by a very simple to use yaml file.

Dodocker was created by the need of creating images independent from the docker.com registry. Nevertheless it is
possible to base your builds on the public docker registry.

Installation
============

You have two options:

1. Build your own environment

Please consulte the README.md file in the example directory. This is a complete setup and a starting
point for creating an environment for building your own Debian and Ubuntu base images.

2. Build within a dodocker image

Run `docker build -t dodocker .` inside the dodocker directory. 

When built you can execute a build with:
docker run -v /var/run/docker.sock:/var/run/docker.sock -ti --rm dodocker


Quick start
===========

The build is defined in a dodocker.yaml file following the
[YAML data structure syntax](http://www.yaml.org/start.html). Every build is described as a list of dictionary
entries where every dictionary is defining a build whereas a build can be done by executing a Dockerfile
or executing a shell action. Generally shell actions should be used only to build the needed bootstrap
images (debian,ubuntu, ...). In this example an nginx image is build, which is dependant on a debian image.
This debian image is build by debootstrap using the docker mkimage script. The nginx image is built by docker
and the provided Dockerfile in the directory images/nginx. The registry image is build by cloning a github
respository and building the image by docker with the included Dockerfile.

Example:

    - image: nginx
      depends: debian-base:jessie
      path: images/nginx
     
    - image: registry:2
      git_url: git@github.com:docker/distribution.git
      path: .

    - image: debian-base:jessie
      path: images/baseimages/docker-mkimage
      shell_action: >
          mkimage.sh -t debian-base:jessie debootstrap
	             --variant=minbase jessie http://ftp.debian.org/debian
		     

Available dodocker.yaml config options
======================================

for shell actions:

    image: name of image
    shell_action: "command to be exected" 
    depends: image name to depend upon (optional)
    tags: [tag1,tag2,...] (optional list of tags)

for Dockerfiles:

    image: name of image
    depends: image name to depend upon (optional)
    path: path/to/directory (for git respositories the repo root is .) 
    file_dep: [file1, file2, dir/file3, ...] (files to watch for changes, optional)
    dockerfile: optional dockerfile
    pull: force a pull for dependant [remote] image (optional, default is false. available when docker_build is true)
    rm: remove intermediate containers after successful build (true (default)/false) 
    tags: [tag1,tag2,...] (optional list of tags)

Building images
===============

Inside the directory that carries the dodocker.yaml file type:

    $ dodocker build

This will call the default `build` task to be run. If a build sub-task errors out, the stdout
from this build is sent to stdout. If you like to generally see the output of your builds, run
build in verbose mode.

    $ dodocker build -v

It is also possible to build images in parallel. A warning though: There seems to be a race
condition within docker to make a build fail from time to time, when running in parallel.
Restarting the build will finish the build eventually.
This will run 4 build processes in parallel:

    $ dodocker build -n 4

Uploading to a private registry
===============================

Before uploading docker images, the registry path has to be set.

    $ dodocker config --set-registry registry.yourdomain.com:443

To allow registry uploads via http or unsigned certificates it is possible to allow insecure
registries:

    $ dodocker config --set-insecure

switch it back to secure only:

    $ dodocker config --set-secure

Settings are saved in a `dodocker.cfg` file in the current directory.

To upload:

    $ dodocker upload

This will push the images to the private registry.


