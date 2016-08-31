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
import base
import unittest
import os
import glob


class TestKTBPackaging(unittest.TestCase):
    builddir = os.path.realpath(os.path.dirname(__file__) + '/../../build')

    def cleandir(self):
        if os.path.exists(self.builddir):
            os.system('rm -rf ' + self.builddir)

    def makepak(self):
        """
        Check that the packaging script works
        """
        import os
        import glob
        os.system(os.path.dirname(__file__) + '/../../package/package.sh')
        self.assertTrue(os.path.exists(self.builddir))
        self.assertTrue(len(glob.glob(self.builddir + '/kavetoolbox-installer*.sh')))
        self.assertTrue(len(glob.glob(self.builddir + '/kavetoolbox-*.tar.gz')))

    def runTest(self):
        """
        Check that the packaging script works
        """
        self.cleandir()
        self.makepak()
        self.cleandir()


if __name__ == "__main__":
    import sys

    verbose = False
    if "--verbose" in sys.argv:
        verbose = True
        sys.argv = [s for s in sys.argv if s != "--verbose"]
    test1 = TestKTBPackaging()
    test1.debug = verbose
    suite = unittest.TestSuite()
    suite.addTest(test1)
    base.run(suite)
