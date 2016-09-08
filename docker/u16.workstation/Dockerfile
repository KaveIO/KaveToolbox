# KaveToolbox 3.0-Beta-Pre on ubuntu 16
FROM kave/kavetoolbox:3.0-Beta-Pre.u16.node
MAINTAINER KAVE <kave@kpmg.com>
RUN apt-get update
RUN wget http://repos:kaverepos@repos.dna.kpmglab.com/noarch/KaveToolbox/3.0-Beta-Pre/kavetoolbox-installer-3.0-Beta-Pre.sh
RUN /bin/bash kavetoolbox-installer-3.0-Beta-Pre.sh --clean-before
