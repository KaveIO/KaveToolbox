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
eclipse.py module: installs eclipse
"""
import os
from kaveinstall import Component, linuxVersion
from kavedefaults.sharedcomponents import java

# ######################  ECLIPSE  ############################


class EclipseComponent(Component):
    """
    Subclass to install eclipse
    """

    def script(self):
        dest = "myeclipse.tar.gz"
        self.copy(self.src_from, dest)
        # eclipse is massive, so untar directly next to destination folder to save space
        self.run("mkdir -p " + self.installDirVersion.rstrip('/') + '_tmp')
        os.chdir(self.installDirVersion.rstrip('/') + '_tmp')
        self.run("tar xzf " + self.tmpdir + '/' + dest)
        if os.path.exists("eclipse"):
            os.system("mv eclipse " + self.installDirVersion)
        elif os.path.exists("opt/eclipse"):
            os.system("mv opt/eclipse " + self.installDirVersion)
        else:
            self.bauk("couldn't find eclipse directory to move!")
        if linuxVersion == "Centos6":
            self.run("echo '-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false' >> "
                     + self.installDir + "/eclipse.ini")
        os.chdir(self.tmpdir)
        self.run("rm -rf " + self.installDirVersion.rstrip('/') + '_tmp')
        return


eclipse = EclipseComponent("eclipse")
eclipse.workstation = True
eclipse.node = False
eclipse.children = {"Centos6": [java],
                    "Centos7": [java],
                    "Ubuntu14": [java],
                    "Ubuntu16": [java]}
eclipse.installSubDir = "eclipse"
eclipse.version = "1.3"
eclipse.src_from = {"arch": "noarch", "suffix": ".tar.gz"}
eclipse.freespace = 500
eclipse.usrspace = 150
eclipse.tempspace = 500
eclipse.env = """
ecl="%%INSTALLDIRVERSION%%"
# Allow mixed 1.X/2.X versions
if [ -z "$pro" ]; then
  if [ ${pro} == 'yes' ]; then
    ecl="%%INSTALLDIRPRO%%"
  fi
fi
# Allow mixed 1.X/2.X versions
if [ ! -d ${ecl} ]; then
  ecl="%%INSTALLDIR%%"
fi

if [ -d ${ecl}  ]; then
    if [[ ":$PATH:" == *":$ecl:"* ]]; then
        true
    else
        export PATH=${ecl}:${PATH}
    fi
fi
"""
eclipse.tests = [('which eclipse > /dev/null', 0, '', '')]


__all__ = ["eclipse"]
