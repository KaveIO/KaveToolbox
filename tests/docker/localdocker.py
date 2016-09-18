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
import subprocess
import sys
import os
from dockerbase import DockerRun


class TestLocalDocker(unittest.TestCase):
    start = "ubuntu:14.04"
    verbose = False
    os_script = {"ubuntu" : ["apt-get update", "apt-get install -y wget curl python python-dev"],
                 "centos" : ["yum clean all", "yum -y install wget curl python python-dev"]}
    script = ["ls -l /opt/hostktb", "/opt/hostktb/scripts/KaveInstall",
              "/opt/KaveToolbox/pro/tests/test.sh /opt/KaveToolbox/pro/tests/installed/all.py"]

    def runTest(self):
        """Run the packaged installer within a docker container.
        Package locally and copy across to the container"""
        topdir = os.path.realpath(os.path.dirname(__file__) + '/../../')
        logdir = '/tmp/log-docker-test-' + self.start.replace(':', "_")
        logfile = logdir + '/log.log'
        os.system('mkdir -p ' + logdir)
        if os.path.exists(logfile):
            os.system('rm -rf ' + logfile)
        os.system('touch ' + logfile)
        stdout = None
        stderr = None
        if not self.verbose:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
        with DockerRun(self.start,
                       ["-v", topdir + ":/opt/hostktb:ro",
                        "-v", logdir + ":" + logdir],
                       stdout=stdout, stderr=stderr) as dock:
            for cmd in self.os_script[self.start.split(':')[0]] + self.script:
                print cmd
                dock.run(cmd, logfile=logfile)
        result = ""
        with open(logfile) as logfilep:
            result = logfilep.read()
        self.assertTrue("Successful install" in result)
        self.assertTrue("installed/definedscripttests ... OK" in result)

if __name__ == "__main__":
    test1 = TestLocalDocker()
    if '--verbose' in sys.argv:
        test1.verbose = True
        sys.argv = [s for s in sys.argv if s != "--verbose"]
    if len(sys.argv) > 1:
        test1.start = sys.argv[1]
    suite = unittest.TestSuite()
    suite.addTest(test1)
    base.run(suite)
