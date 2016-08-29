#!/usr/bin/env python
##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################
"""
kettlecomponent.py module: installs kettle
"""
from kaveinstall import Component
from sharedcomponents import java


class Kettle(Component):

    def script(self):
        dest = "kettle.zip"
        self.copy(self.src_from, dest)
        self.run("unzip -o -q " + dest)
        # default to our hadoop version
        f = open("data-integration/plugins/pentaho-big-data-plugin/plugin.properties")
        lines = f.read()
        f.close()
        f = open("data-integration/plugins/pentaho-big-data-plugin/plugin.properties", "w")
        f.write(lines.replace("active.hadoop.configuration=hadoop-20", "active.hadoop.configuration=hdp22"))
        f.close()
        # default to not show the welcome screen
        addition = """

        #KPMG: workaround for crashing loading screen on Centos!
        dir=$HOME
        if [ -z "$KETTLE_HOME" ]; then
          dir=$HOME/.kettle/
        else
          dir=$KETTLE_HOME
        fi
        if [ -e "$dir/.spoonrc" ]; then
          #OK, do nothing since you already created the file
          dir=$dir
        elif [ -e "$dir" ]; then
          echo "ShowWelcomePageOnStartup=N" > "$dir"/.spoonrc
        else
          mkdir $dir
          echo "ShowWelcomePageOnStartup=N" > "$dir"/.spoonrc
        fi

"""
        f = open("data-integration/spoon.sh")
        lines = f.readlines()
        # fix bug PDI-9977, http://jira.pentaho.com/browse/PDI-9977
        lines = [line.replace("LIBPATH=$BASEDIR/", "LIBPATH=") for line in lines if "cd -" not in line]
        f.close()
        f = open("data-integration/spoon.sh", "w")
        f.write(lines[0])
        f.write(addition)
        f.write('\n'.join(lines[1:]))
        f.close()
        self.run("mv data-integration " + self.installDirVersion)
        return


kettle = Kettle("Kettle")
kettle.doInstall = True
kettle.freespace = 700
kettle.usrspace = 130
kettle.tempspace = 1200
kettle.version = "5.4.0.1-130"
kettle.installSubDir = "kettle"
kettle.src_from = [{'filename': "pdi-ce", 'suffix': ".zip", 'arch': "noarch"},
                   "http://downloads.sourceforge.net/project/pentaho/Data%20Integration/5.4/pdi-ce-5.4.0.1-130.zip"
                   ]
kettle.node = False
kettle.workstation = True
kettle.pre = {"Centos6": ["yum -y install webkitgtk"],
              "Centos7": ["yum -y install webkitgtk"],
              "Ubuntu14": ["apt-get -y install libwebkitgtk-dev"],
              "Ubuntu16": ["apt-get -y install libwebkitgtk-dev"]
              }
kettle.children = {"Centos6": [java],
                   "Centos7": [java],
                   "Ubuntu14": [java],
                   "Ubuntu16": [java]}
kettle.env = """
ket="%%INSTALLDIRVERSION%%"
# Allow mixed 1.X/2.X versions
if [ ! -z "$pro" ]; then
  if [ ${pro} == 'yes' ]; then
    ket="%%INSTALLDIRPRO%%"
  fi
fi

# Allow mixed 1.X/2.X versions
if [ ! -d ${ket} ]; then
  ket="%%INSTALLDIR%%"
fi

if [ -d ${ket}  ]; then
    if [[ ":$PATH:" == *":$ket:"* ]]; then
        true
    else
        export PATH=${ket}:${PATH}
    fi
fi
"""
kettle.tests = [('which spoon.sh > /dev/null', 0, '', '')]


__all__ = ["kettle"]
