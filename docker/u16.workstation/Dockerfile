# KaveToolbox 3.1-Beta-Pre on ubuntu 16
FROM kave/kavetoolbox:3.1-Beta-Pre.u16.node
MAINTAINER KAVE <kave@kpmg.com>
RUN apt-get update
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.1-Beta-Pre/kavetoolbox-installer-3.1-Beta-Pre.sh
RUN rm  -rf /opt/anaconda /opt/eclipse /opt/kettle
RUN /bin/bash kavetoolbox-installer-3.1-Beta-Pre.sh --clean-before
