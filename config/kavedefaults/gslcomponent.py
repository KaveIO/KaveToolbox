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
from kaveinstall import Component

# ######################  pygsl  ############################
gsl = Component("pygsl")
gsl.doInstall = True
gsl.version = "2.1.1"
gsl.src_from = [{"arch": "noarch", "suffix": ".tar.gz"},
                "http://downloads.sourceforge.net/project/pygsl/pygsl/pygsl-2.1.1/pygsl-2.1.1.tar.gz"]
gsl.pre = {"Centos6": ["yum -y install gsl gsl-devel"]}
gsl.pre["Centos7"] = gsl.pre["Centos6"]
gsl.pre["Ubuntu"] = ["apt-get -y install build-essential g++ libgsl0-dev gsl-bin"]
gsl.prewithenv["Centos6"] = [' isinst=`python -c "import pkgutil; '
                             'print pkgutil.find_loader(\\"numpy\\") is not None;"`;'
                             ' if [ ${isinst} == "False" ]; then echo "no scipy/numpy installed,'
                             ' so will not install pygsl,'
                             ' turn on the anaconda installation! '
                             '(was it skipped?) or turn off pygsl." ; exit 1 ; fi ']
gsl.prewithenv["Centos7"] = gsl.prewithenv["Centos6"]
gsl.prewithenv["Ubuntu"] = gsl.prewithenv["Centos6"]

gsl.postwithenv = {"Centos6": [' isinst=`python -c "import pkgutil; '
                               'print pkgutil.find_loader(\\"pygsl\\") is not None;"`;'
                               ' if [ ${isinst} == "False" ]; then cd pygsl-2.1.1; '
                               'python setup.py build; python setup.py install ; fi ']
                   }
gsl.postwithenv["Centos7"] = gsl.postwithenv["Centos6"]
gsl.postwithenv["Ubuntu"] = gsl.postwithenv["Centos6"]
gsl.usrspace = 3
gsl.tempspace = 2
gsl.tests = [("python -c \"import pygsl;\"", 0, '', '')]

__all__ = ["pygsl"]
