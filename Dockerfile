#       __     ___           __
#   ___/ /__  / _ \___  ____/ /_____ ____
#  / _  / _ \/ // / _ \/ __/  '_/ -_) __/
#  \_,_/\___/____/\___/\__/_/\_\\__/_/
#  doDocker (c) 2014-2016 Andreas Elvers
#  n@work Internet Informationssysteme GmbH
#

FROM debian:jessie
ARG DOCKER_ENGINE_VERSION 
ENV DOCKER_ENGINE_VERSION ${DOCKER_ENGINE_VERSION:-1.12.1-0~jessie}
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
RUN echo deb http://apt.dockerproject.org/repo debian-jessie main >/etc/apt/sources.list.d/docker.list
RUN echo deb http://ftp.debian.org/debian jessie-backports main >/etc/apt/sources.list.d/backport.list
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && \
    apt-get -y --no-install-recommends install \
            docker-engine=$DOCKER_ENGINE_VERSION busybox-static python-pip sudo curl git xz-utils make ssh && \
    apt-get -y --no-install-recommends -t jessie-backports install debootstrap

COPY . /dodocker
RUN pip install /dodocker
WORKDIR /build
RUN sed -E -e "s#:/root:#:/build:#" -i /etc/passwd


