# KaveToolbox 3.0-Beta-Pre on ubuntu 16
FROM ubuntu:16.04
MAINTAINER KAVE <kave@kpmg.com>
RUN apt-get update
RUN apt-get install -y wget curl
RUN apt-get install -y python python-dev
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.0-Beta-Pre/kavetoolbox-installer-3.0-Beta-Pre.sh
RUN /bin/bash kavetoolbox-installer-3.0-Beta-Pre.sh --node
