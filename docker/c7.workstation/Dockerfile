# KaveToolbox 3.1-Beta on centos 7
FROM kave/kavetoolbox:3.1-Beta.c7.node
MAINTAINER KAVE <kave@kpmg.com>
RUN yum clean all
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.1-Beta/kavetoolbox-installer-3.1-Beta.sh
RUN rm  -rf /opt/anaconda /opt/eclipse /opt/kettle
RUN /bin/bash kavetoolbox-installer-3.1-Beta.sh --clean-before
