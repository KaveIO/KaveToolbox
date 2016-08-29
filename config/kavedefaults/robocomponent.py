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
robocomponent.py module: installs robomongo
"""
from kaveinstall import Component

robo = Component("robomongo")
robo.doInstall = False  # Don't install at the moment by default, because it doesn't work with mongo 3.0
robo.node = False
robo.workstation = False
robo.version = "0.8.4"
robo.src_from = [{"suffix": ".tar.gz"}]
robo.pre = {"Centos6": ["yum install -y glibc.i686 libstdc++.i686 libgcc.i686"]}
robo.pre["Centos7"] = robo.pre["Centos6"]
robo.pre["Ubuntu14"] = ["apt-get -y install libxcb-icccm4 libxkbcommon-x11-0 "
                        + "libxcb-xkb1 libxcb-render-util0 libxcb-keysyms1 libxcb-image0"]
robo.pre["Ubuntu16"] = robo.pre["Ubuntu14"]
robo.post = {"Centos6": ["yum -y install robomongo-*.rpm"]}
robo.post["Centos7"] = robo.post["Centos6"]
robo.post["Ubuntu14"] = ["dpkg -i robomongo-*.deb"]
robo.post["Ubuntu16"] = robo.post["Ubuntu14"]
robo.usrspace = 40
robo.tempspace = 20
robo.tests = [('which robomongo > /dev/null', 0, '', '')]

__all__ = ["robo"]
