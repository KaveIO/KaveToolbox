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
libInstall.py, base functions and classes for use by the KaveInstaller

Two main pieces expected to be used elsewhere:

fromKPMGRepo(filename,architecture) : find the file for the given os/architecture in a KPMG repo or local mirror
 returns string url if found
 returns None if not found and prints where it looked

class Component(object), instantiated as Component(name), wrapper for generic installation steps
 many implementations will mostly only overwrite the script() method, and set various parameters
 all parameters live in the DefaultConfig.py file which derives classes and sets params of the objects
"""
import time
import string
import os
import sys
import tempfile
#import urllib2
#import httplib
#import commands
import subprocess as sub

#defaults for the repository
#
# NB: the repository server uses a semi-private password only as a means of avoiding robots and reducing DOS attacks
#  this password is intended to be widely known and is used here as an extension of the URL
#
__repo_url__="http://repos:kaverepos@repos.kave.io"
__version__="1.3-Beta"
__main_dir__="KaveToolbox"
__arch__="Centos6"
__mirror_list_file__="/etc/kave/mirror"
__mirror_list__=[]

def repoURL(filename, repo=__repo_url__, arch=__arch__, dir=__main_dir__, ver=__version__):
    """
    Construct the repository address for our code
    """
    if repo[-1]!="/":
        repo=repo+'/'
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
        if mirror[-1]!="/":
            mirror=mirror+'/'
        __mirror_list__.append(mirror)
#
# Wrappers around subprocess
#

def mycmd(cmd):
    proc = sub.Popen(cmd, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
    stdout, stderr = proc.communicate()
    status = proc.returncode
    return status, stdout, stderr


def exitIfFailureQuiet(cmd):
    """
    Run a command, if this command fails raise a RuntimeError.
    Do not print the output of the command while it is running
    cmd: the command to run
    """
    status, output, err = mycmd(cmd)
    if status:
        #exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return status
        #exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return status
        raise RuntimeError(
            "Problem running: \n" + cmd + "\n got:\n\t" + str(status) + "\n from: \n" + output + " stderr: \n" + err)
    return output.strip()


def exitIfFailureLoud(cmd):
    """
    Run a command, if this command fails raise a RuntimeError.
    Echo the progress to stdout while running
    cmd: the command to run
    """
    status = sub.call(cmd, shell=True)
    if status:
        #exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return status
        #exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return status
        raise RuntimeError("Problem running: \n" + cmd + "\n got:\n\t" + str(status))
    return status


def cleanIfFailureQuiet(cmd, directory):
    """
    Run a command, if this command fails, remove a directory and raise a RuntimeError
    Do not print the output of the command while it is running
    cmd: the command to run
    directory: the directory to remove
    """
    status, output, err = mycmd(cmd)
    if status:
        #exception for rpm -i if rpm is already installed
        if (status == 1 or status == 256) and cmd.startswith("rpm "):
            return output.strip()
        #exception for prm -i if rpm is already installed
        if status > 10 and cmd.startswith("wget "):
            return output.strip()
        if len(directory)>4:
            os.system("rm -rf "+directory)
        raise RuntimeError("Problem running: \n"+cmd+"\n got:\n\t"+str(status)+"\n from: \n"+output+" stderr: \n"+err )
    return output.strip()


def cleanIfFailureLoud(cmd, directory):
    """
    Run a command, if this command fails, remove a directory and
    raise a RuntimeError. Echo the progress to stdout while running
    cmd: the command to run
    directory: the directory to remove
    """
    status = sub.call(cmd, shell=True)
    if status:
        #exception for prm -i if rpm is already installed
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

def detectLinuxVersion():
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


linuxVersion = detectLinuxVersion()
InstallTopDir = "/opt"

#
# How to find our files
#

def failoverSource(sources):
    """
    try a list of locations where a file could be, one after the other
    """
    for source in sources:
        if source is None:
            continue
        if source.startswith("ftp:") or (source.startswith("http") and ":" in source):
            #print "checking "+source
            stat, stdout, stderr = mycmd("curl -i -I --keepalive-time 5 " + source)
            if "200 OK" not in stdout and "302 Found" not in stdout:
                #print stdout, stderr, stat
                continue
            return source
        elif os.path.exists(os.path.expanduser(source)):
            return source
    raise IOError("no available sources detected from the options " + sources.__str__())


def fromKPMGrepo(filename, arch=linuxVersion):
    """
    A very useful function for finding a file in our repository
    find the file for the given os/architecture in a KPMG repo or local mirror
         returns string url if found
         returns None if not found and prints where it looked
    """
    #default goes last
    sources = []
    for mirror in __mirror_list__:
        sources.append(repoURL(filename, arch=arch.lower(), repo=mirror))

    sources.append(repoURL(filename, arch=arch.lower()))
    try:
        source = failoverSource(sources)
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
        self.src_from = None
        self.node = True
        self.workstation = True
        self.workstationExtras = None
        self.options = {}
        self.tmpdir = None
        self.topdir = None
        self.toolbox = None
        self.env = ""

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
            raise RuntimeError("Failed to copy from any source "+str(optional_froms))
        afrom = optional_froms
        self.run(copymethods(afrom, dest))
        if not os.path.exists(dest):
            raise IOError("Cannot copy from " + afrom.__str__())
        return True

    def summary(self):
        print self.cname, " Summary :"
        print "    Installing?", self.doInstall
        print "    To:", self.topdir, self.installSubDir, "i.e.:", self.todir()
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
        #default, get file, if it is a .sh file, run it
        f = afrom.split("/")[-1].split('\\')[-1].split("?")[0]
        ext = ""
        if '.' in f:
            ext = '.'.join(f.split(".")[1:])
        dest = self.cname + '.' + ext
        self.copy(self.src_from, dest)
        if ext.endswith(".sh"):
            os.system("chmod a+x " + dest)
            self.run("./" + dest)
        elif ext.endswith(".py"):
            self.run("python ./" + dest)
        return True

    def todir(self):
        """
        It's often complex to interpret exactly where a component will be installed, this method does just that and caches the result.
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


    def install(self, kind="node", tmpdir=None, loud=True):
        """
        Used by the installer, eventually calls the script method
        It is not usual for component derived classes to override this method, since they override the pre, post and script() classes instead
        """
        self.odir = os.path.realpath(os.curdir)
        self.kind = kind
        if self.topdir is None:
            self.topdir = InstallTopDir
        self.tmpdir = tmpdir
        self.loud = loud
        if self.installDir is None:
            self.installDir = self.todir()
        if not self.doInstall:
            return False
        if self.kind is "node" and not self.node:
            return False
        if self.kind is "workstation" and not self.workstation:
            return False
        if self.installDir is not None and os.path.exists(self.installDir) and (self.installDir != self.topdir):
            print "Skipping", self.cname, "because it is already installed"
            print "remove", self.installDir, "if you want to install"
            return self.buildEnv()
        if self.tmpdir is not None:
            os.chdir(self.tmpdir)
        #run prerequisites
        if self.pre is not None and linuxVersion in self.pre:
            for cmd in self.pre[linuxVersion]:
                self.run(cmd)
        #run prerequisites that require the environment
        if self.prewithenv is not None and linuxVersion in self.prewithenv:
            for cmd in self.prewithenv[linuxVersion]:
                self.run("bash -c 'source "+self.toolbox.envscript()+" > /dev/null ;" +cmd+";'")
        #run workstation extras
        if self.kind is "workstation" and self.workstationExtras is not None and linuxVersion in self.workstationExtras:
            for cmd in self.workstationExtras[linuxVersion]:
                self.run(cmd)
        if self.installDir is not None and self.installDir.count('/') > 1:
            self.run("mkdir -p " + os.sep.join(self.installDir.split(os.sep)[:-1]))
        #run script :)
        self.script()
        #run post actions
        if self.post is not None and linuxVersion in self.post:
            for cmd in self.post[linuxVersion]:
                self.run(cmd)
        self.buildEnv()
        #run post actions that require the environment
        if self.postwithenv is not None and linuxVersion in self.postwithenv:
            for cmd in self.postwithenv[linuxVersion]:
                self.run("bash -c 'source "+self.toolbox.envscript()+" > /dev/null ;" +cmd+";'")
        os.chdir(self.odir)
        if self.installDir is not None and self.installDir.count('/') > 1 and os.path.exists(self.installDir):
            self.run("chmod -R a+rx " + self.installDir)
        return True

    def registerToolbox(self, toolbox):
        """
        The method of finding the env script must be known by components, and so the Component which installs
        KaveToolbox itself needs to be remembered and resolved at runtime
        """
        self.toolbox = toolbox

    def buildEnv(self):
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
        loc = self.toolbox.envscript()
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
        f.write(self.env.replace("%%INSTALLDIR%%", self.todir()))
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
            return self._cleanIfFailure(cmd, self.tmpdir)
        self._exitIfFailure(cmd)

    def bauk(self, reason):
        """
        Exit and raise runtime error after cleaning my temporary directory
        """
        if self.tmpdir is not None:
            if os.path.exists(self.tmpdir) and len(self.tmpdir)>4:
                os.system("rm -rf "+self.tmpdir)
        raise RuntimeError(reason)

    def _exitIfFailure(self, cmd):
        if self.loud:
            return exitIfFailureLoud(cmd)
        exitIfFailureQuiet(cmd)

    def _cleanIfFailure(self, cmd, dir):
        if self.loud:
            return cleanIfFailureLoud(cmd, dir)
        cleanIfFailureQuiet(cmd, dir)
