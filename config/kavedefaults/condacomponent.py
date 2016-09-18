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
conda.py module: installs anaconda python
For modifying pip packages, you can create/edit the content of /etc/kave/requirements.txt, start from
the contents of requirements.txt in this folder
"""
import os
from kaveinstall import Component
from kaveinstall import fromKPMGrepo
from kaveinstall import linuxVersion
from sharedcomponents import epel


class Conda(Component):

    def fixstdc(self, fail=True):
        # fix wrong stdc++ linking on ubuntu16
        if linuxVersion in ["Ubuntu16"]:
            if os.path.exists(self.installDirVersion):
                if os.path.exists(self.installDirVersion + '/lib/libstdc++.so.6'):
                    if os.path.exists('/usr/lib/x86_64-linux-gnu/libstdc++.so.6'):
                        self.run('mv -f '
                                 + self.installDirVersion + '/lib/libstdc++.so.6 '
                                 + self.installDirVersion + '/lib/libstdc++.so.6.old')
                        self.run('ln -s '
                                 + '/usr/lib/x86_64-linux-gnu/libstdc++.so.6 '
                                 + self.installDirVersion + '/lib/libstdc++.so.6')
                    elif fail:
                        raise OSError()

    def script(self):
        dest = "./conda.sh"
        self.copy(self.src_from, dest)
        os.system("chmod a+x " + dest)
        # install in batch mode to the requested directory
        self.run(dest + " -b -p " + self.installDirVersion)
        # If a specific python version is required, update now
        # patch for libstdc6, anaconda version not latest version
        self.fixstdc(False)
        self.buildenv()
        if '.' in str(self.python):
            # Attempt to update to this python version
            self.run("bash -c 'source " + self.toolbox.envscript()
                     + " > /dev/null ; conda update --all python="
                     + str(self.python) + "  --yes;'")

    def fillsrc(self):
        """
        Method to fill the src_from in case it must be logical,
        modified to add 2 or 3 to name of file, to match python version for anaconda
        """
        if self.src_from is None:
            return False
        if type(self.src_from) is list:
            # fill version with self.version if suffix is specified but not version
            osf = []
            for s in self.src_from:
                if type(s) is dict and 'version' not in s and 'suffix' in s:
                    s['version'] = self.version
                if type(s) is dict and 'filename' not in s:
                    s['filename'] = self.cname + str(self.python).split('.')[0]
                osf.append(s)
            self.src_from = [fromKPMGrepo(**s) if type(s) is dict else s for s in osf]
        elif type(self.src_from) is dict:
            if 'version' not in self.src_from and 'suffix' in self.src_from:
                self.src_from['version'] = self.version
            if 'filename' not in self.src_from:
                self.src_from['filename'] = self.cname + str(self.python).split('.')[0]
            self.src_from = fromKPMGrepo(**self.src_from)
        return True

conda = Conda(cname="Anaconda")
conda.children = {"Centos6": [epel], "Centos7": [epel]}
conda.pre = {"Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                         'yum -y install libffi* cyrus-sasl* geos*']}
conda.pre["Centos7"] = conda.pre["Centos6"]
conda.pre["Ubuntu14"] = ["apt-get -y install build-essential g++ libffi* "
                         "libsasl2-dev libsasl2-modules-gssapi-mit* cyrus-sasl2-mit* libgeos-dev"]
conda.pre["Ubuntu16"] = conda.pre["Ubuntu14"] + ['apt-get -y install libstdc++6']
conda.postwithenv = {"Centos6": ["conda update conda --yes", "conda install pip --yes",
                                 " if [ -f /etc/kave/requirements.txt ]; "
                                 "then pip install -r /etc/kave/requirements.txt; "
                                 "else pip install -r " + os.path.dirname(__file__) + '/requirements.txt; fi',
                                 "python -c \"import pandas; import seaborn;\"",  # build font cache
                                 "if type krb5-config 2>&1 > /dev/null; then pip install pykerberos; fi"]}
conda.postwithenv["Centos7"] = conda.postwithenv["Centos6"]
conda.postwithenv["Ubuntu14"] = conda.postwithenv["Centos6"]
conda.postwithenv["Ubuntu16"] = conda.postwithenv["Ubuntu14"]
conda.doInstall = True
conda.freespace = 1900
conda.usrspace = 300
conda.tempspace = 300
conda.installSubDir = "anaconda"
conda.python = 2
conda.version = "4.1.1"
conda.src_from = [{"arch": "noarch", "suffix": "-Linux-x86_64.sh"},
                  "https://repo.continuum.io/archive/Anaconda2-4.1.1-Linux-x86_64.sh"]
conda.env = """
ana="%%INSTALLDIRVERSION%%"
# Allow mixed 1.X/2.X versions
if [ ! -z "$pro" ]; then
  if [ ${pro} == 'yes' ]; then
    ana="%%INSTALLDIRPRO%%"
  fi
fi
# Allow mixed 1.X/2.X versions
if [ ! -d ${ana} ]; then
  ana="%%INSTALLDIR%%"
fi

if [ -d ${ana}  ]; then
    if [[ ":$PATH:" == *":$ana/bin:"* ]]; then
        true
    else
        export PATH=${ana}/bin:${PATH}
    fi
fi
"""
conda.tests = [('which python', 0, '%%INSTALLDIRVERSION%%/bin/python\n', ''),
               ("python -c \"import numpy; import seaborn;\"", 0, '', '')]


__all__ = ["conda"]
