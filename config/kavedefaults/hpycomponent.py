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
hpy.py module: installs hpy hadoop python modules
"""
import os
import kaveinstall as li
from kaveinstall import Component
import __future__

class HadoopPy(Component):

    def script(self):
        jdk = self.options["JavaHome"]
        if jdk is None:
            if "JAVA_HOME" in os.environ:
                jdk = os.environ["JAVA_HOME"]
            else:
                stat, jdk, _err = li.mycmd("readlink -f $(which java)")
                jdk = jdk.strip()
                if stat or not jdk.endswith("/jre/bin/java"):
                    print("Warning: could not detect JAVA version, probably you don't have a local hadoop client, " \
                          "so I'm skipping hadoop python libraries, try setting JAVA_HOME manually")
                    jdk = None
                else:
                    jdk = jdk[:-len("/jre/bin/java")]
        hdh = self.options["HadoopHome"]
        if hdh is None:
            if "HADOOP_HOME" in os.environ:
                hdh = os.environ["HADOOP_HOME"]
            else:
                stat, hdh, _err = li.mycmd(" readlink -f $(which hadoop)")
                hdh = hdh.strip()
                if stat or not hdh.endswith("/bin/hadoop"):
                    print("INFO: could not detect hadoop installation, probably you don't have a local hadoop " \
                          "client, so I'm skipping  hadoop python libraries, try setting HADOOP_HOME manually")
                    hdh = None
                else:
                    hdh = hdh[:-len("/bin/hadoop")]

        if hdh is not None and jdk is not None:
            # find hadoop version ...
            stat, hdv, _err = li.mycmd("hadoop version")
            hdv = '.'.join([l for l in hdv.split('\n') if "Hadoop" in l][0].split(" ")[-1].split('.')[:3])
            for ezmodule in self.options["easy_install"]:
                self.run(
                    "bash -c 'source " + self.toolbox.envscript() + " > /dev/null ; export HADOOP_VERSION=" + hdv +
                    "; export JAVA_HOME=" + jdk + "; export HADOOP_HOME=" + hdh
                    + "; export CLASSPATH=$CLASSPATH:`hadoop classpath`; easy_install " +
                    ezmodule + "'")
            for pipmodule in self.options["pip"]:
                self.run(
                    "bash -c 'source " + self.toolbox.envscript() + " > /dev/null ; export HADOOP_VERSION=" + hdv +
                    "; export JAVA_HOME=" + jdk + "; export HADOOP_HOME=" + hdh
                    + "; export CLASSPATH=$CLASSPATH:`hadoop classpath`; pip install " +
                    pipmodule + "'")
        return


hpy = HadoopPy("hadoop_python_modules")
hpy.doInstall = True
hpy.options = {"pip": ["pymongo_hadoop", "pyleus", "mrjob"],  # no pydoop yet, doesn't work very well
               "easy_install": [],  # "-z dumbo"], # dumbo is broken at the moment via easy_install
               "JavaHome": None,
               "HadoopHome": None
               }
hpy.pre = {"Centos6": ["yum -y install boost boost-devel openssl-devel"],
           "Centos7": ["yum -y install boost boost-devel openssl-devel"],
           "Ubuntu14": ["apt-get -y install libboost-python-dev libssl-dev"],
           "Ubuntu16": ["apt-get -y install libboost-python-dev libssl-dev"]
           }
hpy.test = [("python -c \"import mrjob; import pyleus; import pymongo_hadoop;\"", 0, '', '')]


__all__ = ["hpy"]
