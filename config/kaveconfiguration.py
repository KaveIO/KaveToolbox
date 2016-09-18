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
KaveInstall Configuration.

First get all the defaults, the overwrite with custom install if it exists
"""
import os

import kavedefaults as cnf

print "Default config from", cnf.__file__
if os.path.exists('/etc/kave/CustomInstall.py'):
    print "Applying custom configuration from: /etc/kave/CustomInstall.py"
    execfile('/etc/kave/CustomInstall.py')
else:
    print "no custom configuration found, using defaults"

def pick_components(requested_comps):
    """
    pick components from a list of components
    """
    everything = cnf.ordered_components[:]
    if len(requested_comps):
        if 'KaveToolbox' not in requested_comps:
            cnf.toolbox.constinstdir()
        cnames = [c.cname for c in everything]
        fail = [f for f in requested_comps if f not in cnames]
        if len(fail):
            raise NameError("I do not know how to install " + fail.__str__() + " I can only do " + cnames.__str__())
        everything = [e for e in everything if e.cname in requested_comps]
        for e in everything:
            e.doInstall = True
            e.node = True
            e.workstation = True
    return everything

