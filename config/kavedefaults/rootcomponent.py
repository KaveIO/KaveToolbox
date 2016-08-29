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
root.py module: installs root
"""
import os
import sys
import kaveinstall as li
from kaveinstall import Component, linuxVersion
from condacomponent import conda

# Ubuntu fix libpng
libpng = Component("libpng")
libpng.version = "1.5.22"
libpng.doInstall = True
libpng.src_from = {"suffix": ".tar.gz"}
libpng.post = {"Ubuntu": ["bash -c 'if [ ! -e /usr/local/libpng ]; then cd libpng-1.5.22; "
                          + "./configure --prefix=/usr/local/libpng; make; make install;"
                          + " ln -s /usr/local/libpng/lib/libpng15.so.15 /usr/lib/libpng15.so.15; fi;'"]}

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

    def compile(self):
        """
        All the necessary commands to  compile root locally
        """
        if self.options["LowMemoryMode"]:
            print "Compiling ROOT in low memory mode"
            for afile in ["etc/vmc/Makefile.linuxx8664gcc", "config/Makefile.linuxx8664gcc"]:
                f = open(afile)
                l = f.read().replace(" -pipe ", " ")
                f.close()
                f = open(afile, "w")
                f.write(l)
                f.close()
        # patch TMVA::RuleFitParams::CalcFStar function to compile with GCC 5 (C++ 11 enabled)
        self.run("sed -i -e 's/isnan(/TMath::IsNaN(/' tmva/src/RuleFitParams.cxx")
        # need first to compile without python, and then against anaconda python
        self.run("./configure " + self.options["conf"][linuxVersion].replace("--enable-python", ""))
        print "Compiling, may take some time!"
        self.run("make " + self.makeopts)
        # testing
        self.run("bash -c 'source " + self.toolbox.envscript()
                 + "; ./configure " + self.options["conf"][linuxVersion] + "'")
        print "Recompile with python"
        self.run("bash -c 'source " + self.toolbox.envscript() + "; make " + self.makeopts + "'")
        return

    def script(self):
        for ap in sys.path:
            if conda.installSubDir in ap:
                self.bauk(
                    "Cannot compile ROOT because you have already inserted anaconda onto your python path. Please "
                    "touch ~/.nokaveEnv, begin a new shell, and try again")
        # if not test:
        arch_url = li.fromKPMGrepo("root_" + self.version + "_" + linuxVersion.lower() + ".tar.gz")
        noarch_url = li.fromKPMGrepo("root_" + self.version + "_noarch.tar.gz", arch="noarch")
        if self.options["Strategy"] == "Default" or self.options["Strategy"] == "Copy":
            if arch_url:
                self.options["Strategy"] = "Copy"
            else:
                print ("The version you have requested is not available precompiled for this OS,"
                       + "I will try to compile from source")
                self.options["Strategy"] = "Compile"

        if self.options["Strategy"] == "Copy":
            self.src_from = arch_url
        elif self.options["Strategy"] == "Compile" and noarch_url:
            self.src_from = noarch_url
        elif self.options["Strategy"] == "Compile":
            self.src_from = self.src_from + "root_" + self.options["Version"] + ".source.tar.gz"
        else:
            self.bauk(
                "Strategy can either be Default, Compile OR Copy only. Compile takes the source from the root "
                "website, Copy takes the precompiled version from our deployment area, default first tries the copy, "
                "then the compile")
        dest = "root.tar.gz"
        # copy to tmp for unpacking
        self.copy(self.src_from, dest)
        # untar, move to correct location and clean
        self.run("tar xzf " + dest)
        os.system("mkdir -p " + os.sep.join(self.installDirVersion.split(os.sep)[:-1]))
        os.system("mv root " + self.installDirVersion)
        os.chdir(self.installDirVersion)
        if self.options["Strategy"] == "Compile":
            self.compile()
            os.chdir(self.tmpdir)
        os.chdir(self.tmpdir)
        for package in self.options["pip"]:
            self.run(
                "bash -c 'source " + self.toolbox.envscript() + ";"
                + " source " + self.installDirVersion + "/bin/thisroot.sh;"
                + " pip install " + package + "'"
            )
        return


root = RootComponent("root")
root.doInstall = True
root.installSubDir = "root"
root.version = "v5.34.36"
root.options = {"Strategy": "Default",
                "LowMemoryMode": False,
                "conf": {
                    "Centos7": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                               "--enable-mathmore --fail-on-missing",
                    "Centos6": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit  "
                               "--enable-mathmore --fail-on-missing",
                    "Ubuntu": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                              "--enable-mathmore --fail-on-missing"},
                "pip": ["root_numpy", "git+https://github.com/ibab/root_pandas", "rootpy"]
                }
root.src_from = "ftp://root.cern.ch/root/"
root.pre = {"Centos7": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel libglew glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Ubuntu": ["apt-get -y install x11-common libx11-6 x11-utils libX11-dev libgsl0-dev gsl-bin libxpm-dev "
                       "libxft-dev g++ gfortran build-essential g++ libjpeg-turbo8-dev libjpeg8-dev libjpeg8-dev"
                       " libjpeg-dev libtiff5-dev libxml2-dev libssl-dev libgnutls-dev libgmp3-dev libpng12-dev "
                       "libldap2-dev libkrb5-dev freeglut3-dev libfftw3-dev python-dev libmysqlclient-dev libgif-dev "
                       "libiodbc2 libiodbc2-dev libxext-dev libxmu-dev libimlib2 gccxml libxml2 libglew-dev"
                       " glew-utils libc6-dev-i386"
                       ]
            }
root.children = {"Centos6": [glew, glewdev],
                 "Centos7": [],
                 "Ubuntu": [libpng]
                 }
root.freespace = 750
root.usrspace = 300
root.tempspace = 500
root.env = """
#enable the most recent root installation
# Allow mixed 1.X/2.X versions

rt="%%INSTALLDIRVERSION%%"
if [ "$pro" == 'yes' ]; then
  rt="%%INSTALLDIRPRO%%"
elif [ -z "$pro" ]; then
  rt="%%INSTALLDIRPRO%%"
fi
if [ -e "$rt"/bin/thisroot.sh ]; then
    source "$rt"/bin/thisroot.sh
fi
"""
root.tests = [('which root', 0, '%%INSTALLDIRVERSION%%/bin/root\n', ''),
              ("python -c \"import ROOT; ROOT.TBrowser();\"", 0, '', '')]

__all__ = ["root"]
