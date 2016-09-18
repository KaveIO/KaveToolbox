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
The kavedefaults package.
Default configuration parameters and install scripts

We don't recommend you to edit this file. Instead we suggest to create/add configurations to /etc/kave/CustomInstall.py

e.g. adding extra entries like:

#-----------------
import kavedefaults as cnf

# overwrite top install directory
cnf.li.InstallTopDir='/wheretostartinstall'

# add an additional step in the pre-install for the toolbox itself
cnf.toolbox.pre['Centos6'].append("yum -y install lynx")

# never install Eclipse
cnf.eclipse.doInstall=False

# install anaconda into a different subdirectory
cnf.conda.installSubDir='whatever_bro'

# change the configuration options of ROOT to add C++11 support if the latest version of gcc is available:
cnf.root.options["conf"]["Centos6"]=cnf.root.options["conf"]["Centos6"] + " --enable-cxx11"
--fail-on-missing""
#-----------------

For modifying pip packages, you can create/edit the content of /etc/kave/requirements.txt, start from
the contents of requirements.txt in this folder
"""

import kaveinstall as li
from kaveinstall import InstallTopDir
from sharedcomponents import toolbox
from eclipsecomponent import eclipse
from condacomponent import conda
from gslcomponent import gsl
from hpycomponent import hpy
from rootcomponent import root
from robocomponent import robo
from kettlecomponent import kettle
from rcomponent import r


ordered_components = [toolbox, eclipse, kettle, conda, hpy, root, robo, r, gsl]
for __c in ordered_components[1:]:
    __c.register_toolbox(toolbox)
