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
pygsl.py module: installs pygsl
"""
from kaveinstall import Component, mycmd
from condacomponent import conda

# ######################  pygsl 2.1 ############################
gsl1 = Component("pygsl")
gsl1.doInstall = True
gsl1.version = "2.1.1"
gsl1.src_from = [{"arch": "noarch", "suffix": ".tar.gz"},
                 "http://downloads.sourceforge.net/project/pygsl/pygsl/pygsl-2.1.1/pygsl-2.1.1.tar.gz"]
gsl1.pre = {"Centos6": ["yum -y install gsl gsl-devel"]}
gsl1.pre["Centos7"] = gsl1.pre["Centos6"]
gsl1.pre["Ubuntu14"] = ["apt-get -y install build-essential g++ libgsl0-dev gsl-bin"]
gsl1.prewithenv["Centos6"] = [' isinst=`python -c "import pkgutil; '
                              'print(pkgutil.find_loader(\\"numpy\\") is not None);"`;'
                              ' if [ ${isinst} == "False" ]; then echo "no scipy/numpy installed,'
                              ' so will not install pygsl,'
                              ' turn on the anaconda installation! '
                              '(was it skipped?) or turn off pygsl." ; exit 1 ; fi ']
gsl1.prewithenv["Centos7"] = gsl1.prewithenv["Centos6"]
gsl1.prewithenv["Ubuntu14"] = gsl1.prewithenv["Centos6"]
gsl1.prewithenv["Ubuntu16"] = gsl1.prewithenv["Ubuntu14"]

gsl1.postwithenv = {"Centos6": [' isinst=`python -c "import pkgutil; '
                                'print(pkgutil.find_loader(\\"pygsl\\") is not None);"`;'
                                ' if [ ${isinst} == "False" ]; then cd pygsl-*/; '
                                'python setup.py config; python setup.py build; python setup.py install ; fi ']
                    }
gsl1.postwithenv["Centos7"] = gsl1.postwithenv["Centos6"]
gsl1.postwithenv["Ubuntu14"] = gsl1.postwithenv["Centos6"]
gsl1.postwithenv["Ubuntu16"] = gsl1.postwithenv["Ubuntu14"]
gsl1.usrspace = 3
gsl1.tempspace = 2


# ######################  pygsl 2.2 ############################
import copy
# Use for Ubuntu16 only for now, does not work on Centos6 or Ubuntu14
gsl2 = copy.deepcopy(gsl1)
gsl2.version = "2.2.0"
gsl2.src_from = [gsl2.src_from[0],
                 "http://downloads.sourceforge.net/project/pygsl/pygsl/pygsl-2.2.0/pygsl-2.2.0.tar.gz"]
gsl2.prewithenv["Ubuntu16"] = gsl2.prewithenv["Ubuntu14"]
gsl2.pre["Ubuntu16"] = gsl2.pre["Ubuntu14"]
gsl2.postwithenv["Ubuntu16"] = gsl2.postwithenv["Ubuntu14"]

# ######################  pygsl parent ############################


class GslComponent(Component):

    def skipif(self):
        return (conda.installDirVersion in
                mycmd("bash -c 'source " + self.toolbox.envscript()
                      + " > /dev/null ; python -c \"import pygsl; print(pygsl.__file__);\" ;'")[1]
                )

gsl = GslComponent("pygsl")
gsl.doInstall = True
gsl.children = {"Centos6": [gsl1],
                "Centos7": [gsl1],
                "Ubuntu14": [gsl1],
                "Ubuntu16": [gsl2]}
gsl.tests = [("python -c \"import pygsl;\"", 0, '', '')]


__all__ = ["gsl"]
