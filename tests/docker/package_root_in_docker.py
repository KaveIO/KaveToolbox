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
import unittest
import base
import sys
from localdocker import TestLocalDocker


class PackageRoot(TestLocalDocker):
    script = ["ls -l /opt/hostktb",
              "apt-get update",
              "apt-get install -y wget curl",
              "apt-get install -y python python-dev",
              "mkdir -p /etc/kave",
              "echo 'import kavedefaults as cnf; cnf.root.options[\"Strategy\"] "
              + "= \"Compile\";' > /etc/kave/CustomInstall.py",
              "/opt/hostktb/scripts/KaveInstall",
              "/opt/KaveToolbox/pro/tests/test.sh /opt/KaveToolbox/pro/tests/installed/all.py",
              "mkdir /tmp/packroot",
              "/opt/KaveToolbox/pro/scripts/package_root_version.sh /tmp/packroot"
              ]

    def runTest(self):
        """Run the packaged installer within a docker container.
        Package locally and copy across to the container"""
        self.script.append('cp /tmp/packroot/root_*.tar.gz /tmp/log-docker-test-' + self.start.replace(':', "_"))
        self.script.append('chmod a+rwx /tmp/log-docker-test-' + self.start.replace(':', "_") + '/root_*.tar.gz')
        super(PackageRoot, self).runTest()
        import glob
        self.assertTrue(len(glob.glob('/tmp/log-docker-test-'
                                      + self.start.replace(':', "_") + '/root_*'
                                      + self.start.replace(':', "") + '.tar.gz')))

if __name__ == "__main__":
    test1 = PackageRoot()
    if '--verbose' in sys.argv:
        test1.verbose = True
        sys.argv = [s for s in sys.argv if s != "--verbose"]
    if len(sys.argv) > 1:
        test1.start = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(test1)
    base.run(suite)
