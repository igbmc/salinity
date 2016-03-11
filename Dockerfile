FROM debian:7

RUN ln -s /etc/rc2.d /etc/rc.d
RUN apt-get update && apt-get install -y wget

WORKDIR /tmp
RUN wget --no-check-certificate -O install_salt.sh https://bootstrap.saltstack.com
RUN sh install_salt.sh -MX git v2015.5.0

RUN apt-get install -y pkg-config make cmake libssh2-1-dev libhttp-parser-dev libssl-dev libz-dev
RUN wget https://github.com/libgit2/libgit2/archive/v0.22.0.tar.gz
RUN tar xzf v0.22.0.tar.gz
WORKDIR /tmp/libgit2-0.22.0
RUN cmake . && make && make install
RUN apt-get -y install python-pip python-dev libffi-dev && pip install pygit2

ADD resources/master /etc/salt/master
RUN touch /etc/salt/extra_config
ADD resources/minion /etc/salt/minion
RUN mkdir -p /srv/salt && mkdir -p /srv/pillar

RUN service salt-master start && sleep 10 && service salt-minion start && sleep 10 && salt-key -ya minion

WORKDIR /
