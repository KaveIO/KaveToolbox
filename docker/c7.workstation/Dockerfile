# KaveToolbox 3.0-Beta-Pre on centos 7
FROM kave/kavetoolbox:3.0-Beta-Pre.c7.node
MAINTAINER KAVE <kave@kpmg.com>
RUN yum clean all
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.0-Beta-Pre/kavetoolbox-installer-3.0-Beta-Pre.sh
rm  -rf /opt/anaconda /opt/eclipse /opt/kettle
RUN /bin/bash kavetoolbox-installer-3.0-Beta-Pre.sh --clean-before
