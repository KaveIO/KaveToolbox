# KaveToolbox 2.2-Beta on centos 7
FROM kave/kavetoolbox:2.2-Beta.c7.node
MAINTAINER KAVE <kave@kpmg.com>
RUN yum clean all
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/2.2-Beta/kavetoolbox-installer-2.2-Beta.sh
RUN /bin/bash kavetoolbox-installer-2.2-Beta.sh --clean-before
