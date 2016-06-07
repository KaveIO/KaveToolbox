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
import kaveinstall


class TestOneInstalled(unittest.TestCase):
    component = None
    kind = 'workstation'
    def runTest(self):
        """
        Runs a test on one installed piece of software
        """
        if getattr(component, kind):
            component.loud = False
            component.run()



if __name__ == "__main__":

def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestLicense())
    return suite
    base.run(suite())
