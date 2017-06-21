##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
# Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
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
import sys
import __future__
if sys.version_info[0] < 3:
    print("The Python version is %s.%s.%s" % sys.version_info[:3])
    print("These tests require Python 3")
    sys.exit(1)

import unittest
import base
import os
import sys
import kaveinstall as ki


class TestOneInstalledComponent(unittest.TestCase):
    component = None
    kind = 'workstation'

    def id(self):
        return "gaaaah"

    def runTest(self):
        """
        Runs the predefined tests on one installed piece of software
        Each component has a tests list of tuples, component.tests
        these look like: ('command',errcode,'stdout','stderr')
        Tests are always run in the Kave environment

        The command can have the %%INSTALLDIR%%,%%INSTALLDIRPRO%%,%%INSTALLDIRVERSION%%
        directives for search/replace
        """

        self.component.constinstdir()
        # Deal with mixed 2.X / 1.X versions!
        if self.component.cname not in ["KaveToolbox"]:
            # this means the component is installed but a different version (testable)
            if not os.path.exists(self.component.installDirVersion):
                self.component.installDirVersion = self.component.installDirPro
            # this means the KaveToolbox is still 1.X
            if not os.path.exists(self.component.toolbox.installDirVersion):
                self.component.installDirVersion = self.component.installDirPro
            # this means a 1.X version of the component is installed
            if not os.path.exists(self.component.installDirPro):
                self.component.installDirVersion = self.component.installDir
                self.component.installDirPro = self.component.installDir
        # Now, run the tests if this component was supposed to be installed.
        if getattr(self.component, kind) and self.component.doInstall:
            self.component.loud = False
            for ttuple in self.component.tests:
                cmd, rc, sin, sout = ttuple
                ttuple = (
                    self.component.knownreplaces(cmd),
                    rc,
                    self.component.knownreplaces(sin).encode('utf-8'),
                    self.component.knownreplaces(sout).encode('utf-8')
                )
                cmd = ttuple[0]
                script = self.component.toolbox.envscript()
                if os.path.exists(script.replace('/pro/', ki.__version__)):
                    script = script.replace('/pro/', ki.__version__) + " " + ki.__version__
                newtuple = ki.mycmd("bash -c 'source "
                                    + script
                                    + " > /dev/null ;" + cmd + ";'")
                self.assertEquals(ttuple[1:], newtuple, self.component.cname
                                  + ": Unexpected failure with component " + self.component.cname
                                  + ": \n - I was expecting:\n\t" + cmd + ttuple[1:].__str__()
                                  + "\n - But I received:\n\t " + newtuple.__str__())


if __name__ == "__main__":
    suite = unittest.TestSuite()
    kind = 'workstation'
    cnf = None
    with open(os.devnull, 'w') as devnull:
        with base.RedirectStdOut(devnull):
            import kaveconfiguration as kcf
            from kaveconfiguration import cnf
    for skind in ['workstation', 'node']:
        if skind in sys.argv:
            kind = skind
            sys.argv = [s for s in sys.argv if s != skind]
    requested_comps = [a for a in sys.argv[1:] if not a.startswith("-")]
    everything = kcf.pick_components(requested_comps)
    # little constructor to make a test with the same name as the component
    for c in everything:
        ct = None
        exec("""class TestXXX(TestOneInstalledComponent): pass""".replace('XXX', c.cname))
        exec("""ct = TestXXX()""".replace('XXX', c.cname))
        ct.component = c
        ct.kind = kind
        suite.addTest(ct)
    base.run(suite)
