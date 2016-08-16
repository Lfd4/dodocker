FROM debian-base:jessie
ADD sources.list /etc/apt/
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN echo "Europe/Berlin" > /etc/timezone
RUN DEBIAN_FRONTEND=noninteractive dpkg-reconfigure tzdata
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get upgrade
