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
rcomponent.py module: installs r
"""
from kaveinstall import Component
from sharedcomponents import epel, rhrepo

class RComponent(Component):

    def script(self):
        return True


r = RComponent("R")
r.doInstall = True
r.pre = {"Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                     "yum -y install readline-devel",
                     "yum -y install R",
                     "yum -y install R-* --skip-broken"  # not everything installs on Centos6!
                     ],
         "Centos7": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                     "yum -y install readline-devel",
                     "yum -y install texinfo texlive",
                     "yum -y install R",
                     "yum -y install R-* --skip-broken"  # not everything installs on Centos6!
                     ],
         "Ubuntu": ["apt-get -y install libreadline6 libreadline6-dev libc6-dev-i386",
                    "apt-get -y install build-essential g++",
                    "apt-get -y install r-base-dev",
                    "apt-get -y install python-rpy2"
                    ]
         }
r.pre["Centos7"] = r.pre["Centos6"]
r.children = {"Centos6": [epel], "Centos7": [epel, rhrepo]}
r.postwithenv = {"Centos6": ["conda update conda --yes; pip install rpy2"]}
r.postwithenv["Centos7"] = r.postwithenv["Centos6"]
r.postwithenv["Ubuntu"] = ["conda update conda --yes; conda install -c asmeurer rpy2 --yes"]
r.usrspace = 150
r.tempspace = 1
r.test = [("python -c \"import rpy2;\"", 0, '', '')]

__all__ = ["r"]
