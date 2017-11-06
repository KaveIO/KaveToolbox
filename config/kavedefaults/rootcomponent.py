#!/usr/bin/env python
##############################################################################
#
# Copyright 2017 KPMG Advisory N.V. (unless otherwise stated)
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
root.py module: installs root on top of anaconda :)
"""
import os
import sys
import kaveinstall as li
from kaveinstall import Component, linuxVersion, mycmd, installfrom, InstallTopDir
from kavedefaults.condacomponent import conda

# Ubuntu14 fix libpng
libpng = Component("libpng")
libpng.version = "1.5.22"
libpng.doInstall = True
libpng.src_from = {"suffix": ".tar.gz"}
libpng.post = {"Ubuntu14": ["bash -c 'if [ ! -e /usr/local/libpng ]; then cd libpng-1.5.22; "
                            + "./configure --prefix=/usr/local/libpng; make; make install;"
                            + " ln -s /usr/local/libpng/lib/libpng15.so.15 /usr/lib/libpng15.so.15; fi;'"]}
libpng.post["Ubuntu16"] = libpng.post["Ubuntu14"]

# Centos6 Glew Fix
glew = Component("glew")
glew.doInstall = True
glew.version = "1.5.5-1"
glew.src_from = {"suffix": ".el6.x86_64.rpm"}

# Centos6 GlewDev Fix
glewdev = Component("glew-devel")
glewdev.doInstall = True
glewdev.version = "1.5.5-1"
glewdev.pre = {"Centos6": ["yum -y install mesa-libGLU-devel"]}
glewdev.src_from = {"suffix": ".el6.x86_64.rpm"}


class RootComponent(Component):
    ktbpath = os.path.abspath(__file__ + "/../../../")

    def script(self):
        dest = self.tmpdir + "/root-" + root.version + ".tar.gz"
        self.run("mkdir -p " + InstallTopDir + "/" + root.installSubDir)
        self.run("ln -sfT " + root.installSubDir + "-" + root.version + " " +
                 InstallTopDir + "/" + root.installSubDir + "/pro")
        self.copy(self.src_from, dest)
        self.run("tar xzf " + dest + " --no-same-owner -C " + InstallTopDir + "/" + root.installSubDir)
        os.chdir(self.tmpdir)
        self.run("bash -c 'source " + self.toolbox.envscript() + " > /dev/null && " +
                 "export ROOTSYS=" + InstallTopDir + "/" + root.installSubDir + "/pro && "
                 "source \"${ROOTSYS}/bin/thisroot.sh\" && " +
                 "git clone git://github.com/rootpy/root_numpy.git && " +
                 "./root_numpy/setup.py install && " +
                 "git clone https://github.com/ibab/root_pandas.git&& " +
                 "cd root_pandas && python ./setup.py install" + "'")

    def skipif(self):
        return (conda.installDirVersion in
                mycmd("bash -c 'source " + self.toolbox.envscript()
                      + " > /dev/null ; which root ;'")[1]
                )

root = RootComponent("ROOT")
root.doInstall = True
root.version = "6.10.04"
root.installSubDir = "root"
root.src_from = {"arch": str(linuxVersion), "version": root.version, "filename": "root",
                 "suffix": "-" + str(linuxVersion) + "py3.tar.gz"}
root.pre = {"Centos7": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel glew glew-devel qt qt-devel gsl gsl-devel cmake3 gcc-c++ gcc "
                        "binutils clang gcc-gfortran openssl-devel pcre-devel mesa-libGL-devel mesa-libGLU-devel "
                        "cfitsio-devel graphviz-devel avahi-compat-libdns_sd-devel libldap-dev python-devel gsl-static"
                        ],
            "Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel libglew glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Ubuntu14": ["apt-get -y install x11-common libx11-6 x11-utils libX11-dev libgsl0-dev gsl-bin libxpm-dev "
                         "libxft-dev g++ gfortran build-essential g++ libjpeg-turbo8-dev libjpeg8-dev libjpeg8-dev"
                         " libjpeg-dev libtiff5-dev libxml2-dev libssl-dev libgnutls-dev libgmp3-dev libpng12-dev "
                         "libldap2-dev libkrb5-dev freeglut3-dev libfftw3-dev python-dev libmysqlclient-dev libgif-dev "
                         "libiodbc2 libiodbc2-dev libxext-dev libxmu-dev libimlib2 gccxml libxml2 libglew-dev"
                         " glew-utils libc6-dev-i386"
                         ],
            "Ubuntu16": ["apt-get -y install x11-common libx11-6 x11-utils libx11-dev libgsl-dev gsl-bin libxpm-dev "
                         "libxft-dev g++ gfortran build-essential g++ libjpeg-turbo8-dev libjpeg8-dev libjpeg8-dev"
                         " libjpeg-dev libtiff5-dev libxml2-dev libssl-dev libgnutls-dev libgmp3-dev libpng12-dev "
                         "libldap2-dev libkrb5-dev freeglut3-dev libfftw3-dev python-dev libmysqlclient-dev libgif-dev "
                         "libiodbc2 libiodbc2-dev libxext-dev libxmu-dev libimlib2 gccxml libxml2 libglew-dev"
                         " glew-utils libc6-dev-i386 cmake dpkg-dev graphviz-dev libtbb-dev"
                         ]
            }
root.children = {"Centos6": [glew, glewdev, conda],
                 "Centos7": [conda],
                 "Ubuntu14": [libpng, conda],
                 "Ubuntu16": [libpng, conda]
                 }
root.freespace = 2048
root.usrspace = 300
root.tempspace = 1000
root.env = """

export ROOTSYS="/opt/root/pro"
source "${ROOTSYS}/bin/thisroot.sh"

"""
root.tests = [("python -c \"import ROOT; import root_numpy; import root_pandas; ROOT.TBrowser();\"", 0, '', ''),
              ("root -b -q &>/dev/null", 0, '', '')]

__all__ = ["root"]
