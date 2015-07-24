#       __     ___           __
#   ___/ /__  / _ \___  ____/ /_____ ____
#  / _  / _ \/ // / _ \/ __/  '_/ -_) __/
#  \_,_/\___/____/\___/\__/_/\_\\__/_/
#  doDocker (c) 2014-2015 Andreas Elvers
#  n@work Internet Informationssysteme GmbH
#
#  doDocker is based upon pydoit.org 

FROM debian:jessie
RUN echo deb http://ftp.debian.org/debian jessie-backports main >>/etc/apt/sources.list
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install \
   docker.io debootstrap busybox-static python-pip
COPY . /dodocker
RUN pip install /dodocker
RUN mv /dodocker/example /build
WORKDIR /build
ENTRYPOINT /usr/local/bin/dodocker
