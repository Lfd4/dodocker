FROM ubuntu-base:14.04
ADD sources.list /etc/apt/ 
RUN DEBIAN_FRONTEND=noninteractive apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
RUN echo "Europe/Berlin" > /etc/timezone
RUN DEBIAN_FRONTEND=noninteractive dpkg-reconfigure --frontend noninteractive tzdata
