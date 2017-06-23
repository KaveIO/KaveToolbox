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
import os
import sys


class TestInstHelpers(unittest.TestCase):

    def runTest(self):
        """
        Check the functionality of each tiny helper function in the kaveinstall library
        """
        import kaveinstall as ki
        self.assertEqual(ki.repoURL('fn', 'repo', 'arch', 'dir', 'ver'),
                         'repo/arch/dir/ver/fn', 'unexpected output from RepoURL')
        self.assertEqual(ki.mycmd('echo "w00t"'), (0, b'w00t\n', b''),
                         'unexpected output from mycmd')
        self.assertRaises(RuntimeError, ki.throw_on_fail_quiet, 'exit 1')
        self.assertRaises(RuntimeError, ki.throw_on_fail_loud, 'exit 1')
        import tempfile
        tdir = tempfile.mkdtemp()
        self.assertRaises(RuntimeError, ki.clean_on_fail_quiet, 'exit 1', tdir)
        self.assertFalse(os.path.exists(tdir), 'cleaning (quiet) failed to work')
        tdir = tempfile.mkdtemp()
        self.assertRaises(RuntimeError, ki.clean_on_fail_loud, 'exit 1', tdir)
        self.assertFalse(os.path.exists(tdir), 'cleaning (loud) failed to work')
        self.assertTrue(ki.detect_linux_version() in ["Centos7", "Ubuntu16"],
                        'Unexpected OS result!')
        self.assertTrue(len(ki.df('/')) == 6, 'df -P returned strange results!')
        prot = {"http:": "wget", "https:": "wget", "ftp:": "wget", "/tmp": "cp"}
        for p, m in prot.items():
            self.assertTrue(ki.copymethods(p, 'blah').startswith(m), m + ' copymethod not used for ' + p)
        self.assertRaises(IOError,
                          ki.failoversources,
                          ["https://thisisnotawebsite1928918318971736661181818187222"
                           ".kadklhasdaiuqiowehasdhawq.blah/"]
                          )
        self.assertEqual(ki.failoversources(["https://thisisnotawebsite1928918318971736661181818187222"
                                             ".kadklhasdaiuqiowehasdhawq.blah/",
                                             "http://google.com"]), "http://google.com")
        nn = None
        with open(os.devnull, 'w') as devnull:
            with base.RedirectStdOut(devnull):
                nn = ki.fromKPMGrepo('notafilenotafilenotafilenot')
        self.assertTrue(nn is None,
                        "Expected failure of repo file not seen")
        self.assertTrue(ki.fromKPMGrepo('') is not None,
                        "Default repository not accessible")


class TestInstComponent(unittest.TestCase):

    def runTest(self):
        """
        Check the basic functionality of the Component class
        """
        import kaveinstall as ki
        c1 = ki.Component('component1')
        c2 = ki.Component('component2')

        def reset(components):
            for c in components:
                c.status = False
        # Check that dictionaries do not clobber each other
        c1.pre["Centos6"] = ['fiiiish']
        self.assertFalse('Centos6' in c2.pre, "Component dictionaries clobber each other!")
        # Check that default version is picked up
        self.assertTrue(c1.version == ki.__version__, "Auto-version incorrect")
        c1.pre = {}
        # check that children and processing in principle works
        c2.children[ki.detect_linux_version()] = [c1]
        c2.install(loud=False)
        self.assertTrue(c2.status, "c2 not run correctly")
        self.assertTrue(c1.status, "c1 not run correctly as child")
        # Check tempdir cleaning
        reset([c1, c2])
        import tempfile
        tdir = tempfile.mkdtemp()
        os.system('touch ' + tdir + '/testtest')
        c2.install(loud=False, tmpdir=tdir)
        self.assertFalse(os.path.exists(tdir + '/testtest'), 'failed to clean tempdir')
        # Check freespace calculations
        self.assertRaises(OSError, c2.checkadisk, '/', 10000000000000000000000)
        reset([c1, c2])
        c2.freespace = 10000000000000000000000
        self.assertRaises(OSError, c2.install, loud=False, tmpdir=tdir)
        reset([c1, c2])
        # Check workspace/node functions
        c2.freespace = 0
        c2.workstation = False
        c2.node = True
        c1.node = False
        c2.install(kind='workstation', loud=False, tmpdir=tdir)
        self.assertTrue(c2.status == c2.workstation, "c2 ran when it should not have")
        self.assertTrue(c1.status == c2.status, "c1 ran when it should not have")
        reset([c1, c2])
        c2.install(kind='node', loud=False, tmpdir=tdir)
        self.assertTrue(c2.status == c2.node, "c2 didn't run when it should have")
        self.assertTrue(c1.status == c1.node, "c1 ran when it should not have")
        reset([c1, c2])
        # Now only do things which do not try and download anything!
        c1.src_from = ["http://nonoondoandondnosd193810938901813.kajsdjasld.dsdsa",
                       {'filename': ''}]
        c1.fillsrc()
        self.assertTrue(type(c1.src_from[-1]) is str, "failed to interpret src_from dictionary")
        self.assertTrue(ki.__version__ in c1.src_from[-1], "failed to interpret src_from version")
        if os.path.exists(tdir):
            os.system('rm -rf ' + tdir)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestInstHelpers())
    suite.addTest(TestInstComponent())
    return suite


if __name__ == "__main__":
    base.run(suite())
