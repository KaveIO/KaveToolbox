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
"""
import os
from kaveinstall import Component


class Conda(Component):

    def script(self):
        dest = "./conda.sh"
        self.copy(self.src_from, dest)
        os.system("chmod a+x " + dest)
        # install in batch mode to the requested directory
        self.run(dest + " -b -p " + self.installDirVersion)
        self.buildenv()

conda = Conda(cname="anaconda")
conda.pre = {"Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                         'yum -y install epel-release', 'yum clean all',
                         'yum -y install libffi* cyrus-sasl* geos*']}
conda.pre["Centos7"] = conda.pre["Centos6"]
conda.pre["Ubuntu"] = ["apt-get -y install build-essential g++ libffi* "
                       "libsasl2-dev libsasl2-modules-gssapi-mit* cyrus-sasl2-mit* libgeos-dev"]
conda.postwithenv = {"Centos6": ["conda update conda --yes", "conda install pip --yes",
                                 "pip install delorean seaborn pygal mpld3 ",
                                 "pip install cairosvg pyhs2 shapely descartes",
                                 "pip install pyproj folium vincent pam",
                                 "pip install py4j",
                                 "pip install pymongo",
                                 "if type krb5-config 2>&1 > /dev/null; then pip install pykerberos; fi",
                                 " if [  ! -z \"$ROOTSYS\" ] ; then pip install rootpy ; pip install root_numpy;"
                                 + " pip install git+https://github.com/ibab/root_pandas; fi "]}
conda.postwithenv["Centos7"] = conda.postwithenv["Centos6"]
conda.postwithenv["Ubuntu"] = conda.postwithenv["Centos6"]
conda.doInstall = True
conda.freespace = 1500
conda.usrspace = 300
conda.tempspace = 300
conda.installSubDir = "anaconda"
conda.version = "2.4.1"
conda.src_from = [{"arch": "noarch", "suffix": "-Linux-x86_64.sh"},
                  "https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3"
                  ".ssl.cf1.rackcdn.com/Anaconda2-2.4.1-Linux-x86_64.sh"]
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
