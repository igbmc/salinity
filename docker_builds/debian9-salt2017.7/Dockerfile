#
#
#
FROM debian:9

RUN ln -s /etc/rc2.d /etc/rc.d
RUN apt-get update
RUN apt-get install -y wget gnupg2
RUN echo "deb http://repo.saltstack.com/apt/debian/9/amd64/2017.7 stretch main" >> /etc/apt/sources.list.d/saltstack.list
RUN wget -O - https://repo.saltstack.com/apt/debian/9/amd64/2017.7/SALTSTACK-GPG-KEY.pub | apt-key add -
RUN apt-get update

# Adding support for GitFS
RUN apt-get install -y pkg-config make cmake libssh2-1-dev libhttp-parser-dev libssl-dev libz-dev python-pip python-dev libffi-dev
WORKDIR /tmp
RUN wget https://github.com/libgit2/libgit2/archive/v0.21.3.tar.gz
RUN tar xzf v0.21.3.tar.gz
WORKDIR /tmp/libgit2-0.21.3
RUN cmake . && make && make install
RUN ldconfig
RUN pip install pygit2==0.21.3

# Installing Salt with static version : same for debian:7 and debian:8
RUN apt-get install -y  salt-minion salt-master

# Configure Salt server and client
ADD resources/master /etc/salt/master
RUN touch /etc/salt/extra_config
ADD resources/minion /etc/salt/minion
RUN mkdir -p /srv/salt && mkdir -p /srv/pillar

RUN service salt-master start && sleep 10 && service salt-minion start && sleep 10 && salt-key -ya minion

WORKDIR /
