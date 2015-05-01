#!/usr/bin/env python
##############################################################################
#
# Copyright 2015 KPMG N.V. (unless otherwise stated)
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
KaveInstall Configuration, stores the installer parameters
this is a full python file, so you can edit it to include
any python object or complicated logical syntax, including checking
if directories exist, even.

Please do not git-add back any such local changes to the repo
"""
import inspect
import os
import sys

myfilename = inspect.getframeinfo(inspect.currentframe()).filename
myinstallfrom = os.path.realpath(os.path.dirname(myfilename))
sys.path.append(myinstallfrom)

import DefaultConfig as cnf

if os.path.exists("/etc/kave/CustomInstall.py"):
    execfile("/etc/kave/CustomInstall.py")


    # http://www.rackspace.com/knowledge_center/article/install-the-epel-ius-and-remi-repositories-on-centos-and-red-hat