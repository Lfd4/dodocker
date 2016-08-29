========
dodocker
========

Overview
========

dodocker is a dependency based build tool for docker images. It supports uploading 
built images to a private registry. It is based upon
[doit task management & automation tool](http://pydoit.org/). 
The build configuration is described in a simple to use yaml file.
Dodocker was originally created by the need of creating images independent from the docker.com registry.
Nevertheless your are totally free to base your build configuration on the public docker registry.

Installation
============

1. Easy install

Run `eval $(docker run --rm nawork/dodocker dodocker alias)`. This will pull the dodocker image from 
the public registry and execute the alias command of dodocker. You can now access
the command `dodocker` within your current shell. The command runs in its own temporary container.
2. Building your own dodocker

Check out dodocker from github. In the dodocker directory run `docker build -t nawork/dodocker .`. 
After building is complete activate the alias with `eval $(docker run --rm nawork/dodocker dodocker alias)`
3. Install dodocker as a python package

Please consulte the README.md file in the example directory. It describes a complete setup
and is a starting point for creating an environment for integrating dodocker in a building 
environment.

Quick start
===========

The build hierarchy is defined in a dodocker.yaml file following the
[YAML data structure syntax](http://www.yaml.org/start.html). 

For the impatient:

Assuming you activated the dodocker alias, create an empty directory and call `dodocker quickstart`.
This will copy a quickstart project to the empty directory. It contains build jobs for base images like
Debian, Apline and Ubuntu as well as the docker registry.

```
$ dodocker quickstart
$ ls
dodocker.yaml  images  README.md
```

Dodocker YAML
=============

The `dodocker.yaml` file containers a list of rules to build images. Every rule is a mapping that contains
key/value pairs.

Let's consider this example dodocker.yaml:

    - image: nginx
      depends: debian-base:jessie
      path: images/nginx
     
    - image: registry:2
      git_url: git@github.com:docker/distribution.git tags/v2.5.0
      path: .

    - image: debian-base:jessie
      path: images/baseimages/docker-mkimage
      shell_action: >
          mkimage.sh -t debian-base:jessie debootstrap
	             --variant=minbase jessie http://ftp.debian.org/debian

* A dodocker.yaml is described as a sequence of mapping nodes.
* Every definition has a required image name and optional tag
* Path is pointing to the image source directory. Path is always relative to the directory containing
  the dodocker.yaml
* A build is by default based upon a Dockerfile with is located in the directory path is pointing to.
* An alternative to Dockerfile based builds are shell-actions. These should only be used
  to contruct base images which are not buildable via Dockerfiles. For shell actions dodocker expects
  the shell script to create an image that has a name and tag like described in the dodocker.yaml. 
* Add a `depends` to an image to create a dependency on some other image
* Add `git_url` to fetch a branch (master is default), tag or commit from a git url. Please note that
  path is relative to the checked out source in this case.

Available dodocker.yaml config options
======================================

for shell actions:

    image: name of image
    path: path/to/directory 
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

Image to be build can be specified as arguments. Only these images and those they are depending upon
will be built. The image name as stated in the dodocker.yaml is to be used as parameter to dodocker build

    $ dodocker build jwilder/nginx-proxy mystuff/apache2.4-php-mysql

It is also possible to build images in parallel. This will run 4 build processes in parallel as long as
dependencies are allowing for:

    $ dodocker build -n 4

Uploading to a private registry
===============================

Before uploading docker images, the registry path has to be set. In this example uploads are
configured to be pushed to registry.yourdomain.com using https and expecting a valid certificate.

    $ dodocker config --set-registry registry.yourdomain.com:443
    $ dodocker config --set-secure

To allow registry uploads via http or unsigned certificates it is possible to allow insecure
registries:

    $ dodocker config --set-insecure

switch it back to secure only:

    $ dodocker config --set-secure

Settings are saved in a `dodocker.cfg` file in the current directory.

To upload:

    $ dodocker upload

This will push all images defined in dodocker.yaml to the private registry.


