##############################################################################
#
# Copyright 2016 KPMG N.V. (unless otherwise stated)
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
kaveinstall.py, base functions and classes for use by the KaveInstaller

Two main pieces expected to be used elsewhere:

fromKPMGRepo(filename,architecture) : find the file for the given os/architecture in a KPMG repo or local mirror
 returns string url if found
 returns None if not found and prints where it looked

class Component(object), instantiated as Component(name), wrapper for generic installation steps
 many implementations will mostly only overwrite the script() method, and set various parameters
 all parameters live in the kavedefaults.py file which derives classes and sets params of the objects
"""
import time
import string
import os
import sys
import tempfile
import subprocess as sub

# defaults for the repository
#
# NB: the repository server uses a semi-private password only as a means of avoiding robots and reducing DOS attacks
#  this password is intended to be widely known and is used here as an extension of the URL
#
__repo_url__ = "http://repos:kaverepos@repos.kave.io"
__version__ = "2.0-Beta"
__main_dir__ = "KaveToolbox"
__arch__ = "Centos6"
__mirror_list_file__ = "/etc/kave/mirror"
__mirror_list__ = []


def repoURL(filename, repo=__repo_url__, arch=__arch__, dir=__main_dir__, ver=None):
    """
    Construct the repository address for our code
    """
    if ver is None:
        ver = __version__
    if repo[-1] != "/":
        repo = repo + '/'
    return repo + arch.lower() + "/" + dir + "/" + ver + "/" + filename

#
# Automatically load mirror list
# Always add a '/' if there is no trailing '/'

if os.path.exists(__mirror_list_file__):
    f = open(__mirror_list_file__)
    ls = f.readlines()
    f.close()
    for mirror in ls:
        mirror = mirror.strip()
        if not len(mirror):
            continue
        if mirror[-1] != "/":
            mirror = mirror + '/'
        __mirror_list__.append(mirror)

#
# Wrappers around subprocess
#


def mycmd(cmd):
    proc = sub.Popen(cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = proc.communicate()
    status = proc.returncode
    return status, stdout, stderr


def throw_on_fail_quiet(cmd):
    """
    Run a command, if this command fails raise a RuntimeError.
    Do not print the output of the command while it is running
    cmd: the command to run
    """
    status, output, err = mycmd(cmd)
    if status:
        # exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return status
        # exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return status
        raise RuntimeError(
            "Problem running: \n" + cmd + "\n got:\n\t" + str(status) + "\n from: \n" + output + " stderr: \n" + err)
    return output.strip()


def throw_on_fail_loud(cmd):
    """
    Run a command, if this command fails raise a RuntimeError.
    Echo the progress to stdout while running
    cmd: the command to run
    """
    status = sub.call(cmd, shell=True)
    if status:
        # exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return status
        # exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return status
        raise RuntimeError("Problem running: \n" + cmd + "\n got:\n\t" + str(status))
    return status


def clean_on_fail_quiet(cmd, directory):
    """
    Run a command, if this command fails, remove a directory and raise a RuntimeError
    Do not print the output of the command while it is running
    cmd: the command to run
    directory: the directory to remove
    """
    status, output, err = mycmd(cmd)
    if status:
        # exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return output.strip()
        # exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return output.strip()
        if len(directory) > 4:
            os.system("rm -rf " + directory)
        raise RuntimeError("Problem running: \n" + cmd + "\n got:\n\t" +
                           str(status) + "\n from: \n" + output + " stderr: \n" + err)
    return output.strip()


def clean_on_fail_loud(cmd, directory):
    """
    Run a command, if this command fails, remove a directory and
    raise a RuntimeError. Echo the progress to stdout while running
    cmd: the command to run
    directory: the directory to remove
    """
    status = sub.call(cmd, shell=True)
    if status:
        # exception for prm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return status
        if status > 10 and cmd.startswith("wget "):
            return status
        os.system("rm -rf " + directory)
        raise RuntimeError("Problem running: \n" + cmd + "\n got:\n\t" + str(status))
    return status


#
# Simple helper functions
#

def detect_linux_version():
    status, output, err = mycmd("uname -r")
    if status:
        raise RuntimeError("Problem detecting linux version: \n" + cmd + "\n got:\n\t" + str(
            status) + "\n from: \n" + output + " stderr: \n" + err)
    if "el6" in output:
        return "Centos6"
    elif "el7" in output:
        return "Centos7"
    else:
        status2, output2, err = mycmd("lsb_release -a")
        if not status2 and "Ubuntu" in output2:
            return "Ubuntu"
    return output


def df(filename, options=[]):
    filename = os.path.realpath(filename)
    while not os.path.exists(filename) and len(filename) > 1:
        filename = os.path.realpath(filename + '/../')
    if not os.path.exists(filename):
        raise OSError("File does not exist so I cannot check anything for " + filename)
    _df = sub.Popen(["df", filename] + options, stdout=sub.PIPE)
    try:
        output = _df.communicate()[0]
    except:
        raise OSError("Problem retrieving diskspace for " + filename)
    return output.split("\n")[1].split()


def installfrom():
    minstallfrom = os.path.realpath(os.sep.join(__file__.split(os.sep)[:-2]))
    if minstallfrom == "":
        minstallfrom = ".."
    if minstallfrom.endswith("scripts"):
        minstallfrom = minstallfrom[:-len("scripts")]
    if minstallfrom.endswith("config"):
        minstallfrom = minstallfrom[:-len("config")]
    return minstallfrom


def copymethods(source, destination):
    if "drive.google" in source:
        return installfrom() + '/bin/gdown.pl "' + source + '" ' + destination
    if source.startswith("ftp:") or (source.startswith("http") and ":" in source):
        return "wget '" + source + "' -O " + destination
    if os.path.exists(os.path.expanduser(source)):
        return "cp " + source + " " + destination
    raise IOError("no method to copy from " + source)


linuxVersion = detect_linux_version()
InstallTopDir = "/opt"

#
# How to find our files
#


def failoversources(sources):
    """
    try a list of locations where a file could be, one after the other
    """
    for source in sources:
        if source is None:
            continue
        if source.startswith("ftp:") or (source.startswith("http") and ":" in source):
            # print "checking "+source
            stat, stdout, stderr = mycmd("curl -i -I --keepalive-time 5 " + source)
            if "200 OK" not in stdout and "302 Found" not in stdout:
                # print stdout, stderr, stat
                continue
            return source
        elif os.path.exists(os.path.expanduser(source)):
            return source
    raise IOError("no available sources detected from the options " + sources.__str__())


def fromKPMGrepo(filename, arch=linuxVersion, version=None, suffix=None):
    """
    A very useful function for finding a file in our repository
    find the file for the given os/architecture in a KPMG repo or local mirror
         returns string url if found
         returns None if not found and prints where it looked
    arch = linux architecture/version to find default current OS
    version = version of software
    ext = file extension, used to create filename
    filename + version + extension = filename
    """
    # default goes last
    if version:
        filename = filename + '-' + version
    if suffix:
        filename = filename + suffix
    sources = []
    for mirror in __mirror_list__:
        sources.append(repoURL(filename, arch=arch.lower(), repo=mirror))

    sources.append(repoURL(filename, arch=arch.lower()))
    try:
        source = failoversources(sources)
        return source
    except IOError:
        print sources, "no file", filename, "found"

    return None


#
# Main installer class
#


class Component(object):
    """
    class wrapper for generic install scripts
    cname, component name
    installDir, where to install
    install() can be overwriten with custom python
    pre { OS: [] }, prerequisites to the true install, like installing component libraries
    doInstall, install it or not
    script(), simple script to run if possible, overwrite with custom python in derived classes
    any other options variables used in the script, might be either { OS: {"OptName":optval} } or just {"option",
    "value"}
    node, install if on a node?
    src_from, where to get the source from

    """

    def __init__(self, cname):
        self.cname = cname
        self.loud = True
        self.pre = {}
        self.prewithenv = {}
        self.post = {}
        self.postwithenv = {}
        self.doInstall = True
        self.installSubDir = None
        self.installDir = None
        self.installDirVersion = None
        self.installDirPro = None
        self.cleanBefore = False  # remove install directory
        self.cleanAfter = False  # remove older installations
        self.skipIfDiskFull = False  # skip installation if disk is full
        self.cleanIfDiskFull = False  # skip installation if disk is full
        self.installDirPro = None
        self.src_from = None
        self.node = True
        self.workstation = True
        self.workstationExtras = None
        self.options = {}
        self.tmpdir = None
        self.topdir = None
        self.toolbox = None
        self.version = __version__
        self.freespace = 0  # /installdir size requirement in mb
        self.tempspace = 0  # /tmp size requirement in mb
        self.usrspace = 0  # /usr size requirement in mb
        self.env = ""
        self.children = {}
        self.status = False

    def fillsrc(self):
        """
        Method to fill the src_from in case it must be logical
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
                    s['filename'] = self.cname
                osf.append(s)
            self.src_from = [fromKPMGrepo(**s) if type(s) is dict else s for s in osf]
        elif type(self.src_from) is dict:
            if 'version' not in self.src_from and 'suffix' in self.src_from:
                self.src_from['version'] = self.version
            if 'filename' not in self.src_from:
                self.src_from['filename'] = self.cname
            self.src_from = fromKPMGrepo(**self.src_from)
        return True

    def copy(self, optional_froms, dest):
        if type(optional_froms) is list:
            for afrom in optional_froms:
                if afrom is None:
                    continue
                try:
                    return self.copy(afrom, dest)
                except RuntimeError, IOError:
                    print "Failed to copy from", afrom, "retry next source"
                    continue
            raise RuntimeError("Failed to copy from any source " + str(optional_froms))
        afrom = optional_froms
        self.run(copymethods(afrom, dest))
        if not os.path.exists(dest):
            raise IOError("Cannot copy from " + afrom.__str__())
        return True

    def summary(self):
        print self.cname, " Summary :"
        print "    Installing?", self.doInstall
        print "    To:", self.topdir, self.installSubDir, "i.e.:", self.todir()
        print "    Version:", self.version
        print "    From:", self.src_from
        print "    Nodes?:", self.node
        print "    Workstations?:", self.workstation
        print "    Workstations Extras:", self.workstationExtras
        print "    Pre:", self.pre
        print "    Pre with environment file:", self.prewithenv
        print "    Post:", self.post
        print "    Post with environment file:", self.postwithenv
        print "    Options:", self.options
        print "----------------------------"

    def script(self):
        """
        Script method, if self.src_from is set then download it from the repo
        execute downloaded shell scripts or python files, that is all
        Complicated installs will overwrite this class.
        """
        if self.src_from is None:
            return False
        afrom = self.src_from
        if type(afrom) is list:
            afrom = afrom[0]
        # default, get file, if it is a .sh file, run it
        ext = ""
        try:
            f = afrom.split("/")[-1].split('\\')[-1].split("?")[0]
            if '.' in f:
                ext = '.'.join(f.split(".")[1:])
        except AttributeError:
            print "warning, could not determine file extension, does the download location exist?"
        dest = self.cname + '.' + ext
        self.copy(self.src_from, dest)
        if ext.endswith(".sh"):
            os.system("chmod a+x " + dest)
            self.run("./" + dest)
        elif ext.endswith(".py"):
            self.run("python ./" + dest)
        elif ext.endswith(".tar.gz"):
            self.run("tar -xzf ./" + dest)
        elif ext.endswith(".tar"):
            self.run("tar -xf ./" + dest)
        elif ext.endswith(".rpm"):
            self.run("rpm -i ./" + dest)
        return True

    def todir(self):
        """
        It's often complex to interpret exactly where a component will be installed,
        this method does just that and caches the result.
        """
        if self.installDir is not None:
            return self.installDir
        if self.installSubDir is not None and self.topdir is not None:
            return (self.topdir + os.sep + self.installSubDir).replace("//", "/")
        if self.topdir is not None:
            return self.topdir
        if self.topdir is None and self.installSubDir is not None:
            return (InstallTopDir + os.sep + self.installSubDir).replace("//", "/")
        if self.topdir is None:
            return InstallTopDir
        return None

    def checkadisk(self, disk, space):
        """
        Check that so much space is available on a disk containing a given directory
        """
        # check inodes
        free_inodes = df(disk, ['-i'])
        free = int(free_inodes[3])
        if free < 100:
            raise OSError("No free inodes on mount point " + free_inodes[-1] + " to install " + self.cname)
        free_space = df(disk, ['-m'])
        free = int(free_space[3])
        if free < space:
            raise OSError("Not enough space on mount point " + free_space[-1] + " to install " + self.cname
                          + " (" + disk + "). Skip the installation, cleanup, or add more disk space, an additional "
                          + str(space - free) + " MB is needed")
        return free_space[-1]

    def clean(self, others_only=False):
        if self.installDir is not None and os.path.exists(self.installDir):
            if not others_only:
                print "Force-cleaning installation directory as requested"
                if len(self.installDirPro) > 4 and os.path.islink(self.installDirPro):
                    self.run("rm -f " + self.installDirPro)
                if len(self.installDirPro) > 4 and os.path.exists(self.installDirPro):
                    self.run("rm -rf " + self.installDirPro)
                if len(self.installDirVersion) > 4 and os.path.exists(self.installDirVersion):
                    self.run("rm -rf " + self.installDirVersion)
                if (len(self.installDir) > 4 and (os.path.exists(self.installDir)
                                                  and (os.path.realpath(self.installDir)
                                                       != os.path.realpath(self.topdir)))):
                    self.run("rm -rf " + self.installDir)
            else:
                print "Force-cleaning obsolete installations as requested"
                import glob
                dirs = glob.glob(self.installDir + '/*')
                cleaning = [os.path.realpath(d) for d in dirs if os.path.realpath(d)
                            not in [os.path.realpath(self.installDir),
                                    os.path.realpath(self.installDirVersion),
                                    os.path.realpath(self.installDirPro)]]
                cleaning = [d for d in cleaning if len(d) > 4 and os.path.isdir(d)]
                [self.run("rm -rf " + d) for d in cleaning if os.path.isdir(d)]
            return True
        return False

    def __checkdloop(self, mounts):
        """
        Loop to check for disk space, expect OSError if not enough space
        """
        checked_mounts = {}
        for k, v in mounts.iteritems():
            mnt = self.checkadisk(k, v)
            try:
                checked_mounts[mnt] = checked_mounts[mnt] + v
            except KeyError:
                checked_mounts[mnt] = v
        if len(checked_mounts) < len(mounts):
            [self.checkadisk(k, v) for k, v in checked_mounts.iteritems()]
        return checked_mounts

    def install(self, kind="node", tmpdir=None, loud=True):
        """
        Used by the installer, eventually calls the script method
        It is not usual for component derived classes to override this method,
        since they override the pre, post and script() classes instead
        """
        self.odir = os.path.realpath(os.curdir)
        self.kind = kind
        if self.topdir is None:
            self.topdir = InstallTopDir
        self.tmpdir = tmpdir
        self.loud = loud
        if self.installDir is None:
            self.installDir = self.todir()
            self.installDirVersion = (self.installDir + os.sep + self.version).replace("//", "/")
            self.installDirPro = (self.installDir + os.sep + 'pro').replace("//", "/")
        if not self.doInstall:
            return False
        if self.kind is "node" and not self.node:
            return False
        if self.kind is "workstation" and not self.workstation:
            return False
        if self.installDir is not None and os.path.exists(self.installDir) and (self.installDir != self.topdir):
            if self.cleanBefore:
                self.clean()
            if os.path.isdir(self.installDirVersion):
                print "Skipping", self.cname, "because this version is already installed"
                print "remove", self.installDirVersion, "if you want to force re-install"
                self.buildenv()
                return self.__install_end_actions()
                # Detect previous KTB installation and skip
            if (os.path.exists(self.installDir) and not os.path.exists(self.installDirPro)
                    and not os.path.islink(self.installDirPro) and len(os.listdir(self.installDir))):
                print "Skipping", self.cname, "because a 1.X-KTB version was already installed"
                print "remove", self.installDir, "if you want to force re-install"
                return False
        ##############################
        # Check disk space
        ##############################
        free_disk = None
        mounts = {}
        if self.freespace:
            if self.installDir:
                mounts[self.installDir] = self.freespace
            else:
                mounts['/'] = self.freespace
        if self.tempspace:
            if self.tmpdir:
                mounts[self.tmpdir] = self.tempspace
            else:
                mounts['/tmp'] = self.tempspace
        if self.usrspace:
            mounts['/usr'] = self.usrspace
        # Check these mountpoints and clean if requested
        try:
            self.__checkdloop(mounts)
        except OSError as e:
            if self.cleanIfDiskFull:
                self.clean()
        # Check again and skip if requested
        try:
            self.__checkdloop(mounts)
        except OSError as e:
            if self.skipIfDiskFull:
                print "Skipping", self.cname, "because of insufficient disk space"
                print e
                return self.buildenv()
            raise e
        ##############################
        # Install children
        ##############################
        if self.children is not None and linuxVersion in self.children:
            for child in self.children[linuxVersion]:
                if not child.status:
                    child.install(kind=self.kind, tmpdir=self.tmpdir, loud=self.loud)
        ##############################
        # run prerequisites
        ##############################
        if self.pre is not None and linuxVersion in self.pre:
            for cmd in self.pre[linuxVersion]:
                self.run(cmd)
        # run prerequisites that require the environment
        if self.prewithenv is not None and linuxVersion in self.prewithenv:
            for cmd in self.prewithenv[linuxVersion]:
                self.run("bash -c 'source " + self.toolbox.envscript() + " > /dev/null ;" + cmd + ";'")
        # run workstation extras
        if (self.kind is "workstation" and (self.workstationExtras is not None
                                            and linuxVersion in self.workstationExtras)):
            for cmd in self.workstationExtras[linuxVersion]:
                self.run(cmd)
        if self.installDir is not None and self.installDirVersion.count('/') > 1:
            self.run("mkdir -p " + os.sep.join(self.installDirVersion.split(os.sep)[:-1]))
        # Find the places to download from
        self.fillsrc()
        # run script :)
        self.script()
        # run post actions
        if self.post is not None and linuxVersion in self.post:
            for cmd in self.post[linuxVersion]:
                self.run(cmd)
        self.buildenv()
        # run post actions that require the environment
        if self.postwithenv is not None and linuxVersion in self.postwithenv:
            for cmd in self.postwithenv[linuxVersion]:
                self.run("bash -c 'source " + self.toolbox.envscript() + " > /dev/null ;" + cmd + ";'")
        os.chdir(self.odir)
        if self.installDir is not None and self.installDir.count('/') > 1 and os.path.exists(self.installDir):
            self.run("chmod -R a+rx " + self.installDir)
        return self.__install_end_actions()

    def __install_end_actions(self):
        self.status = True
        # create pro softlink
        if self.installDir is not None:
            if ((os.path.exists(self.installDirPro) or os.path.islink(self.installDirPro))
                    and os.path.exists(self.installDirVersion)):
                os.system("rm " + self.installDirPro)
            if os.path.exists(self.installDirVersion):
                os.system("ln -s " + self.installDirVersion + " " + self.installDirPro)

        # clean the temporary directory of files I created
        if self.tmpdir is not None:
            if os.path.exists(self.tmpdir) and len(self.tmpdir) > 4:
                os.system("rm -rf " + self.tmpdir + '/*')
        if self.installDir is not None and os.path.exists(self.installDir) and (self.installDir != self.topdir):
            if self.cleanAfter:
                self.clean(others_only=True)
        return True

    def register_toolbox(self, toolbox):
        """
        The method of finding the env script must be known by components, and so the Component which installs
        KaveToolbox itself needs to be remembered and resolved at runtime
        """
        self.toolbox = toolbox

    def buildenv(self):
        """
        Build env adds to the standard environment script the contents of self.env
        in order to build a static env file (fastest approach) this method can autoreplace the key
        to determine the installed package directory
        self.env.replace("%%INSTALLDIR%%", self.todir())
        """
        if self.toolbox is None:
            return
        if not len(self.env):
            return
        loc = self.toolbox.envscript().split()[0]
        if not len(loc):
            return
        f = open(loc)
        lines = f.readlines()
        f.close()
        beforelines = []
        afterlines = []
        for line in lines:
            if line.strip() == "## Begin " + self.cname:
                break
            beforelines.append(line)
        found = False
        for line in lines:
            if line.strip() == "## End " + self.cname:
                found = True
                continue
            if not found:
                continue
            afterlines.append(line)
        f = open(loc, 'w')
        f.write(''.join(beforelines))
        f.write("## Begin " + self.cname + '\n')
        f.write('#\n')
        e = self.env.replace("%%INSTALLDIR%%", self.installDir)
        e = e.replace("%%INSTALLDIRPRO%%", self.installDirPro)
        e = e.replace("%%INSTALLDIRVERSION%%", self.installDirVersion)
        e = e.replace("%%VERSION%%", self.version)
        f.write(e)
        f.write('#\n')
        f.write("## End " + self.cname + '\n')
        f.write(''.join(afterlines))
        f.close()
        return True

    def run(self, cmd):
        """
        Intelligently run a command, either cleaning or exiting if the command fails
        """
        if self.tmpdir is not None and os.path.exists(self.tmpdir):
            return self._clean_on_fail(cmd, self.tmpdir)
        self._throw_on_fail(cmd)

    def bauk(self, reason):
        """
        Exit and raise runtime error after cleaning my temporary directory
        """
        if self.tmpdir is not None:
            if os.path.exists(self.tmpdir) and len(self.tmpdir) > 4:
                os.system("rm -rf " + self.tmpdir)
        raise RuntimeError(reason)

    def _throw_on_fail(self, cmd):
        if self.loud:
            return throw_on_fail_loud(cmd)
        throw_on_fail_quiet(cmd)

    def _clean_on_fail(self, cmd, dir):
        if self.loud:
            return clean_on_fail_loud(cmd, dir)
        clean_on_fail_quiet(cmd, dir)
