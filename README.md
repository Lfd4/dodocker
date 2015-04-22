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

for Dockerfiles:
image: name of image
docker_build: true (mandatory for building a Dockerfile)
depends: image name to depend upon (optional)
path: /path/to/directory
file_dep: [file1, file2, dir/file3, ...] (files to watch for changes, optional)
dockerfile: optional dockerfile
