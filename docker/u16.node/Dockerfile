# KaveToolbox 3.6-Beta on ubuntu 16
FROM ubuntu:xenial
MAINTAINER KAVE <kave@kpmg.com>
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y
RUN apt-get install -y wget curl python python-dev
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.6-Beta/kavetoolbox-installer-3.6-Beta.sh
RUN /bin/bash kavetoolbox-installer-3.6-Beta.sh --node
