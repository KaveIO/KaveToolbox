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
sparkcomponent.py module: installs spark
"""
import os
from kaveinstall import Component, InstallTopDir

class SparkComponent(Component):
    
    def script(self):
        dest = self.tmpdir + "/spark-" + spark.version + ".tgz"
        self.run("mkdir -p " + InstallTopDir + "/" + self.installSubDir)
        self.run("ln -sfT " + spark.installSubDir + "-" + spark.version + " " +
                 InstallTopDir + "/" + self.installSubDir + "/pro")        
        self.copy(self.src_from, dest)
        self.run("tar xzf " + dest + " --no-same-owner -C " + InstallTopDir + "/" + spark.installSubDir)
        os.chdir(InstallTopDir + "/" + self.installSubDir + "/pro")
        self.run("build/mvn -DskipTests -DrecompileMode=all clean package")
        return

spark = SparkComponent("spark")
spark.doInstall = False  # Don't install at the moment by default
spark.node = False
spark.workstation = False
spark.version = "2.1.0"
spark.installSubDir = "spark"
spark.src_from = ["http://archive.apache.org/dist/spark/spark-" 
                  + spark.version + "/spark-" + spark.version + ".tgz"]

#spark.usrspace = 40
#spark.tempspace = 20
#spark.tests = [('which sparkmongo > /dev/null', 0, '', '')]

#spark.env = """
##Begin SPARK

#export SPARK_HOME=" "


## End SPARK
#"""


__all__ = ["spark"]



