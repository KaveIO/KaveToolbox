# KaveToolbox 3.0-Beta on ubuntu 14
FROM kave/kavetoolbox:3.0-Beta.u14.node
MAINTAINER KAVE <kave@kpmg.com>
RUN apt-get update
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.0-Beta/kavetoolbox-installer-3.0-Beta.sh
RUN rm  -rf /opt/anaconda /opt/eclipse /opt/kettle
RUN /bin/bash kavetoolbox-installer-3.0-Beta.sh --clean-before
