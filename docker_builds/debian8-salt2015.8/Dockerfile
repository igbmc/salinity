#
#
#
FROM debian:8

# Place une variable d'environnement pour indiquer qu'on tourne dans un container docker
# Ceci est utile notamment pour systemd
ENV container docker
# Indique à l'installateur de paquets Debian de ne pas utilsier le mode interactif (qui est celui par défaut)
ARG DEBIAN_FRONTEND=noninteractive

RUN ln -s /etc/rc2.d /etc/rc.d
RUN apt-get update \
&& apt-get install -y wget ca-certificates apt-transport-https
RUN echo "deb https://repo.saltstack.com/apt/debian/8/amd64/2015.8 jessie main" >> /etc/apt/sources.list.d/saltstack.list \
&& wget -O - https://repo.saltstack.com/apt/debian/8/amd64/2015.8/SALTSTACK-GPG-KEY.pub | apt-key add - \
&& apt-get update

# Adding support for GitFS
RUN apt-get install -y pkg-config make cmake libssh2-1-dev libhttp-parser-dev libssl-dev libz-dev python-pip python-dev libffi-dev \
&& pip install pip --upgrade
WORKDIR /tmp
RUN wget https://github.com/libgit2/libgit2/archive/v0.21.3.tar.gz \
&& tar xzf v0.21.3.tar.gz
WORKDIR /tmp/libgit2-0.21.3
RUN cmake . \
&& make \
&& make install \
&& ldconfig \
&& pip install pygit2==0.21.3
RUN rm -Rf /tmp/libgit2-0.21.3

# Installing Salt
RUN apt-get install -y salt-minion salt-master

# Configure Salt server and client
ADD resources/master /etc/salt/master
ADD resources/pki/master/minions/minion /etc/salt/pki/master/minions/minion
RUN touch /etc/salt/extra_config

ADD resources/minion /etc/salt/minion
ADD resources/pki/minion/minion.pem /etc/salt/pki/minion/minion.pem
ADD resources/pki/minion/minion.pub /etc/salt/pki/minion/minion.pub

RUN mkdir -p /srv/salt && mkdir -p /srv/pillar
RUN service salt-master start && service salt-minion start

WORKDIR /
