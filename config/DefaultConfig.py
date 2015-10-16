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
Default configuration parameters and install scripts

We don't recommend you to edit this file. Instead we suggest to create/add configurations to /etc/kave/CustomConfig.py

e.g. adding extra entries like:

#-----------------
import DefaultConfig as cnf

# overwrite top install directory
cnf.li.InstallTopDir='/wheretostartinstall'

# add an additional step in the pre-install for the toolbox itself
cnf.toolbox.pre['Centos6'].append("yum -y install lynx")

# never install Eclipse
cnf.eclipse.doInstall=False

# install anaconda into a different subdirectory
cnf.conda.installSubDir='whatever_bro'

# change the configuration options of ROOT to add C++11 support if the latest version of gcc is available:
cnf.root.options["conf"]["Centos6"]=""linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11
--fail-on-missing""
#-----------------
"""
import os
import sys
import libInstall as li
from libInstall import InstallTopDir, Component, linuxVersion

#top level directory under where to keep all KAVE software
li.InstallTopDir = "/opt"


#######################  KAVETOOLBOX ITSELF ############################


class Toolbox(Component):
    """
    Wrapper class for overwriting certain parts of the default installer
    """

    def installfrom(self):
        minstallfrom = os.path.realpath(os.sep.join(__file__.split(os.sep)[:-2]))
        if minstallfrom == "":
            minstallfrom = ".."
        if minstallfrom.endswith("scripts"):
            minstallfrom = minstallfrom[:-len("scripts")]
        if minstallfrom.endswith("config"):
            minstallfrom = minstallfrom[:-len("config")]
        return minstallfrom

    def envscript(self):
        try:
            guess_installed = self.todir() + os.sep + "scripts" + os.sep + "KaveEnv.sh"
        except TypeError:
            guess_installed = self.todir() + os.sep + "scripts" + os.sep + "KaveEnv.sh"
        if os.path.exists(guess_installed):
            return guess_installed
        installfrom = self.installfrom()
        return installfrom + os.sep + "scripts" + os.sep + "KaveEnv.sh"

    def buildEnv(self):
        prepend = False
        rest = []
        scriptloc = self.envscript()
        #recreate env script in case it totally does not exist, or somehow is missing the intro...
        if not os.path.exists(scriptloc) and os.path.exists(self.todir() + '/scripts/'):
            prepend = True
        elif os.path.exists(scriptloc):
            f = open(scriptloc)
            rest = f.readlines()
            f.close()
            if not len(rest) > 1:
                prepend = True
            elif not rest[0].startswith("#!/bin/bash"):
                prepend = True
        if prepend and os.path.exists(os.path.dirname(scriptloc)):
            f = open(scriptloc, 'w')
            f.write("""#!/bin/bash

# Simple script to set up the KAVE environment
# called automatically from /etc/profile.d if the installer has
# been run.

# touch ~/.nokaveEnv to disable the automatic calling of the script

# touch .kaveEnv to force automatic calling of the script unless .nokaveEnv is present

# touch ~/.nokaveBanner to disable printing the banner

"""
                    )
            f.write(''.join(rest))
            f.close()
        return super(Toolbox, self).buildEnv()

    def script(self):
        #don't include the .git directory
        if ".git" in self.installfrom():
            raise NameError(
                "Sorry, I cannot be installed from a directory which includes '.git' in the name! Can you please "
                "download/copy to a different directory and try again")
        self.run(
            "rsync -rv --exclude=.git --exclude=.project --exclude=.pydevproject --exclude=.pyc " + self.installfrom(

            ) + "/ " + self.todir())
        #self.run("mv ./"+self.installfrom().rstrip('/').split('/')[-1]+" "+self.installDir)
        f = open(self.installfrom() + os.sep + "scripts" + os.sep + "autoKaveEnv.sh")
        l = f.read()
        f.close()
        l = l.replace("%ENVSCRIPT%", self.envscript())
        #overwrite if it exists
        if not os.access("/etc/profile.d", os.W_OK):
            self.bauk(
                "cannot write into /etc/profile.d, this means you are not running with root privilages. Run again as "
                "root, or turn off the explicit toolbox.doInstall in Configuration.py")
        f = open("/etc/profile.d/kave.sh", "w")
        f.write(l)
        f.close()
        #add to bash.bashrc for non-interactive&non-login shells
        l = "#!/bin/bash\n"
        if os.path.exists("/etc/bash.bashrc"):
            f = open("/etc/bash.bashrc")
            l = f.read()
            f.close()
        if "/etc/profile.d/kave.sh" not in l:
            f = open("/etc/bash.bashrc", "w")
            if not len(l.strip()):
                l = "#!/bin/bash"
            f.write(l)
            f.write("""
if [ -e /etc/profile.d/kave.sh ]; then
    source /etc/profile.d/kave.sh
fi
""")
            f.close()
        #set default wallpaper on workstations
        if self.setwallpaper is True or (self.kind=='workstation' and self.setwallpaper in ['default','workstation']):
            if linuxVersion.lower().startswith("centos"):
                self.run('gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string '
                         +'--set /desktop/gnome/background/picture_filename '+self.todir()+'/figs/KAVE_wp'+str(self.wallpaperselect)+'.png')
                self.run('gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string '
                         +' --set /desktop/gnome/background/picture_options centered')
            if linuxVersion.lower().startswith("ubuntu"):
                os.makedirs('/etc/xdg/xfce4/xfconf/xfce-perchannel-xml',0755)
                self.run('cp '+os.path.join(os.path.realpath(__file__),'xfce4-desktop.xml')+ ' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/')
        return True


toolbox = Toolbox("KaveToolbox")
toolbox.doInstall = True
toolbox.installSubDir = "KaveToolbox"
toolbox.workstationExtras = {"Centos6": ['yum -y groupinstall "Desktop" "Desktop Platform" "X Window System" "Fonts" --exclude=NetworkManager\\*',
                                         'yum -y install tigervnc-server firefox'],
                             "Centos7": ['yum -y groupinstall "Desktop" "Desktop Platform" "X Window System" "Fonts"  --exclude=NetworkManager\\*',
                                         'yum -y install tigervnc-server firefox'],
                             "Ubuntu": ['if ! type vncserver 2>&1 > /dev/null ; then '# apt-get -y install dictionaries-common; '
                                        #+'/usr/share/debconf/fix_db.pl; '#apt-get -y install -f; '
                                        +'apt-get -y install gnome-core xfce4 xfce4-goodies firefox;'
                                        + 'apt-get -y install tightvncserver; '
                                        +'fi;']
                             }
toolbox.setwallpaper='default' #wallpaper if it is a workstation type
toolbox.wallpaperselect=0 #a number between 0 and 9
toolbox.pre = {"Centos6": ["yum -y install vim emacs wget curl zip unzip tar gzip rsync git"],
               "Centos7": ["yum -y install vim emacs wget curl zip unzip tar gzip rsync git"],
               "Ubuntu": ['apt-get -y install dictionaries-common',
                          "apt-get -y install vim emacs wget curl zip unzip tar gzip rsync git"]
               }
toolbox.registerToolbox(toolbox)
toolbox.env = """

ban='yes'
if [ $TERM != "dumb" ]; then
    if [ ! -z "$HOME" ]; then
        if [ -d "$HOME" ]; then
            if [ -e  "$HOME"/.nokaveBanner ]; then
                ban='no'
            fi
        fi
    fi
    if [ ${ban} == 'yes' ]; then
        if [ -e %%INSTALLDIR%%/Welcome.banner ]; then
            cat %%INSTALLDIR%%/Welcome.banner
        fi
    fi
fi

export KAVETOOLBOX=%%INSTALLDIR%%

#only add directories to path if they are not already there!
if [[ ":$PATH:" == *":%%INSTALLDIR%%/bin:%%INSTALLDIR%%/scripts:"* ]]; then
    true
else
    export PATH=%%INSTALLDIR%%"/bin:"%%INSTALLDIR%%"/scripts:"${PATH}
fi

if [[ ":$PYTHONPATH:" == *":%%INSTALLDIR%%/python:"* ]]; then
    true
else
    export PYTHONPATH=%%INSTALLDIR%%"/python:"${PYTHONPATH}
fi

"""


#######################  ECLIPSE  ############################

class EclipseComponent(Component):
    """
    Subclass to install eclipse
    """

    def script(self):
        dest = "myeclipse.tar.gz"
        self.copy(self.src_from, dest)
        self.run("tar xvzf " + dest)
        if os.path.exists("eclipse"):
            os.system("mv eclipse " + self.installDir)
        elif os.path.exists("opt/eclipse"):
            os.system("mv opt/eclipse " + self.installDir)
        else:
            self.bauk("couldn't find eclipse directory to move!")
        if linuxVersion == "Centos6":
            self.run("echo '-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false' >> " + self.installDir + "/eclipse.ini")
        return


eclipse = EclipseComponent("Eclipse")
eclipse.workstation = True
eclipse.node = False
eclipse.pre = {"Centos6": ["yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel"],
               "Centos7": ["yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel"],
               "Ubuntu": ["apt-get -y install default-jre default-jdk "]
               }
eclipse.installSubDir = "eclipse"
eclipse.src_from = li.fromKPMGrepo("eclipse.tar.gz", arch="noarch")
eclipse.registerToolbox(toolbox)
eclipse.env = """
ecl="%%INSTALLDIR%%"
if [ -d ${ecl}  ]; then
    if [[ ":$PATH:" == *":$ecl:"* ]]; then
        true
    else
        export PATH=${ecl}:${PATH}
    fi
fi
"""

#######################  ANACONDA  ############################

class Conda(Component):
    def script(self):
        dest = "./conda.sh"
        self.copy(self.src_from, dest)
        os.system("chmod a+x " + dest)
        #install in batch mode to the requested directory
        self.run(dest + " -b -p " + self.installDir)
        self.buildEnv()

conda = Conda(cname="anaconda")
conda.pre={"Centos6":['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                      'yum -y install epel-release',
                      'yum -y install libffi* cyrus-sasl* geos*']}
conda.pre["Centos7"]=conda.pre["Centos6"]
conda.pre["Ubuntu"]=["apt-get -y install build-essential g++ libffi* libsasl2-dev libsasl2-modules-gssapi-mit* cyrus-sasl2-mit* libgeos-dev"]
conda.postwithenv={"Centos6" : ["conda update conda --yes","conda install pip --yes",
                                "pip install delorean seaborn pygal mpld3 cairosvg pyhs2 shapely descartes pyproj folium vincent pam"]}
conda.postwithenv["Centos7"]=conda.postwithenv["Centos6"]
conda.postwithenv["Ubuntu"]=conda.postwithenv["Centos6"]
conda.doInstall = True
conda.installSubDir = "anaconda"
conda.registerToolbox(toolbox)
conda.src_from = [li.fromKPMGrepo("Anaconda-2.2.0-Linux-x86_64.sh", arch="noarch"),
                  "https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.2.0-Linux-x86_64.sh"]
conda.env = """
ana="%%INSTALLDIR%%"
if [ -d ${ana}  ]; then
    if [[ ":$PATH:" == *":$ana/bin:"* ]]; then
        true
    else
        export PATH=${ana}/bin:${PATH}
    fi
fi
"""

#######################  Hadoop modules  ############################

class HadoopPy(Component):
    def script(self):
        jdk = self.options["JavaHome"]
        if jdk is None:
            if "JAVA_HOME" in os.environ:
                jdk = os.environ["JAVA_HOME"]
            else:
                stat, jdk, err = li.mycmd("readlink -f $(which java)")
                jdk = jdk.strip()
                if stat or not jdk.endswith("/jre/bin/java"):
                    print "Warning: could not detect JAVA version, probably you don't have a local hadoop client, " \
                          "so I'm skipping hadoop python libraries, try setting JAVA_HOME manually"
                    jdk = None
                else:
                    jdk = jdk[:-len("/jre/bin/java")]
        hdh = self.options["HadoopHome"]
        if hdh is None:
            if "HADOOP_HOME" in os.environ:
                hdh = os.environ["HADOOP_HOME"]
            else:
                stat, hdh, err = li.mycmd(" readlink -f $(which hadoop)")
                hdh = hdh.strip()
                if stat or not hdh.endswith("/bin/hadoop"):
                    print "INFO: could not detect hadoop installation, probably you don't have a local hadoop " \
                          "client, so I'm skipping  hadoop python libraries, try setting HADOOP_HOME manually"
                    hdh = None
                else:
                    hdh = hdh[:-len("/bin/hadoop")]

        if hdh is not None and jdk is not None:
            #find hadoop version ...
            stat, hdv, err = li.mycmd("hadoop version")
            hdv = '.'.join([l for l in hdv.split('\n') if "Hadoop" in l][0].split(" ")[-1].split('.')[:3])
            for ezmodule in self.options["easy_install"]:
                self.run(
                    "bash -c 'source " + self.toolbox.envscript() + " > /dev/null ; export HADOOP_VERSION=" + hdv +
                    "; export JAVA_HOME=" + jdk + "; export HADOOP_HOME=" + hdh
                    + "; export CLASSPATH=$CLASSPATH:`hadoop classpath`; easy_install " +
                    ezmodule + "'")
            for pipmodule in self.options["pip"]:
                self.run(
                    "bash -c 'source " + self.toolbox.envscript() + " > /dev/null ; export HADOOP_VERSION=" + hdv +
                    "; export JAVA_HOME=" + jdk + "; export HADOOP_HOME=" + hdh
                    + "; export CLASSPATH=$CLASSPATH:`hadoop classpath`; pip install " +
                    pipmodule + "'")
        return


hpy = HadoopPy("hadoop_python_modules")
hpy.doInstall = True
hpy.options = {"pip": ["pymongo_hadoop", "pyleus", "mrjob"],  #no pydoop yet, doesn't work very well
               "easy_install": ["-z dumbo"],
               "JavaHome": None,
               "HadoopHome": None
               }
hpy.pre = {"Centos6": ["yum -y install boost boost-devel openssl-devel"],
           "Centos7": ["yum -y install boost boost-devel openssl-devel"],
           "Ubuntu": ["apt-get -y install libboost-python-dev libssl-dev"]
           }
hpy.registerToolbox(toolbox)

#######################  ROOT  ############################

class RootComponent(Component):
    def compile(self):
        """
        All the necessary commands to  compile root locally
        """
        if self.options["LowMemoryMode"]:
            print "Compiling ROOT in low memory mode"
            for afile in ["etc/vmc/Makefile.linuxx8664gcc", "config/Makefile.linuxx8664gcc"]:
                f = open(afile)
                l = f.read().replace(" -pipe ", " ")
                f.close()
                f = open(afile, "w")
                f.write(l)
                f.close()
        #need first to compile without python, and then against anaconda python
        self.run("./configure " + self.options["conf"][linuxVersion].replace("--enable-python", ""))
        print "Compiling, may take some time!"
        out = self.run("make")
        #testing
        self.run(
            "bash -c 'source " + self.toolbox.envscript() + "; ./configure " + self.options["conf"][linuxVersion] + "'")
        print "Recompile with python"
        self.run("bash -c 'source " + self.toolbox.envscript() + "; make'")
        return

    def todir(self):
        """
        Override destination directory to insert version...
        """
        if self.installDir is not None:
            return self.installDir
        if self.installSubDir is not None and self.topdir is not None:
            return self.topdir + os.sep + self.installSubDir + os.sep + self.options["Version"]
        if self.topdir is not None:
            return self.topdir + os.sep + self.options["Version"]
        return None


    def script(self):
        for ap in sys.path:
            if conda.installSubDir in ap:
                self.bauk(
                    "Cannot compile ROOT because you have already inserted anaconda onto your python path. Please "
                    "touch ~/.nokaveEnv, begin a new shell, and try again")
        #if not test:
        arch_url = li.fromKPMGrepo("root_" + self.options["Version"] + "_" + linuxVersion.lower() + ".tar.gz")
        noarch_url = li.fromKPMGrepo("root_" + self.options["Version"] + "_noarch.tar.gz", arch="noarch")
        if self.options["Strategy"] == "Default" or self.options["Strategy"] == "Copy":
            if arch_url:
                self.options["Strategy"] = "Copy"
            else:
                print "The version you have requested is not available precompiled for this OS, I will try to compile " \
                      "" \
                      "from source"
                self.options["Strategy"] = "Compile"

        if self.options["Strategy"] == "Copy":
            self.src_from = arch_url
        elif self.options["Strategy"] == "Compile" and noarch_url:
            self.src_from = noarch_url
        elif self.options["Strategy"] == "Compile":
            self.src_from = self.src_from + "root_" + self.options["Version"] + ".source.tar.gz"
        else:
            self.bauk(
                "Strategy can either be Default, Compile OR Copy only. Compile takes the source from the root "
                "website, Copy takes the precompiled version from our deployment area, default first tries the copy, "
                "then the compile")
        dest = "root.tar.gz"
        #copy to tmp for unpacking
        self.copy(self.src_from, dest)
        #untar, move to correct location and clean
        self.run("tar xvzf " + dest)
        os.system("mkdir -p " + os.sep.join(self.installDir.split(os.sep)[:-1]))
        os.system("mv root " + self.installDir)
        os.chdir(self.installDir)
        if self.options["Strategy"] == "Compile":
            self.compile()
            os.chdir(self.tmpdir)
        if self.options["UpdateSoftlink"]:
            linkat = self.topdir + os.sep + 'root' + os.sep + "pro"
            if os.path.exists(linkat):
                os.system("rm " + linkat)
            os.system("ln -s " + self.installDir + " " + linkat)
        os.chdir(self.tmpdir)
        for package in self.options["pip"]:
            self.run(
                "bash -c 'source " + self.toolbox.envscript() + "; source " + self.installDir + "/bin/thisroot.sh; "
                                                                                                "pip install " +
                package + "'")
        return


root = RootComponent("root")
root.doInstall = True
root.installSubDir = "root"
root.options = {"Strategy": "Default",
                "Version": "v5.34.21",
                "UpdateSoftlink": True,
                "LowMemoryMode": False,
                "conf": {
                    "Centos7": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                               "--enable-mathmore --fail-on-missing",
                    "Centos6": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit  "
                               "--enable-mathmore --fail-on-missing",
                    "Ubuntu": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                              "--enable-mathmore --fail-on-missing"},
                "pip": ["root_numpy", "git+https://github.com/ibab/root_pandas"]
                }
root.src_from = "ftp://root.cern.ch/root/"
root.pre = {"Centos7": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        #"wget https://oss.oracle.com/ol6/RPM-GPG-KEY-oracle",
                        #"rpm --import RPM-GPG-KEY-oracle",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        #"wget https://oss.oracle.com/ol6/RPM-GPG-KEY-oracle",
                        #"rpm --import RPM-GPG-KEY-oracle",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel libglew glew glew-devel qt qt-devel gsl gsl-devel",
                        "wget " + li.fromKPMGrepo("glew-1.5.5-1.el6.x86_64.rpm", arch="centos6"),
                        #http://dl.fedoraproject.org/pub/epel/6/x86_64/glew-1.5.5-1.el6.x86_64.rpm
                        "wget " + li.fromKPMGrepo("glew-devel-1.5.5-1.el6.x86_64.rpm", arch="centos6"),
                        #http://dl.fedoraproject.org/pub/epel/6/x86_64/glew-devel-1.5.5-1.el6.x86_64.rpm",
                        "rpm -i glew-1.5.5-1.el6.x86_64.rpm",
                        "rpm -i glew-devel-1.5.5-1.el6.x86_64.rpm"
                        ],
            "Ubuntu": [
                "apt-get -y install x11-common libx11-6 x11-utils libX11-dev libgsl0-dev gsl-bin libxpm-dev "
                "libxft-dev g++ gfortran build-essential g++ libjpeg-turbo8-dev libjpeg8-dev libjpeg8-dev libjpeg-dev "
                " libtiff5-dev libxml2-dev libssl-dev libgnutls-dev libgmp3-dev libpng12-dev libldap2-dev libkrb5-dev "
                "freeglut3-dev libfftw3-dev python-dev libmysqlclient-dev libgif-dev libiodbc2 libiodbc2-dev "
                "libxext-dev libxmu-dev libimlib2 gccxml libxml2 libglew-dev glew-utils libc6-dev-i386",
                "wget " + li.fromKPMGrepo("libpng-1.5.22.tar.gz", arch="ubuntu"),
                "tar xzf libpng-1.5.22.tar.gz",
                ("bash -c 'if [ ! -e /usr/local/libpng ]; then cd libpng-1.5.22; ./configure --prefix=/usr/local/libpng; make; make install;"
                 + " ln -s /usr/local/libpng/lib/libpng15.so.15 /usr/lib/libpng15.so.15; fi;'")
                ]
            }

root.registerToolbox(toolbox)
root.env = """
#enable the most recent root installation
topd="/opt"
if [ -e ${topd}/root/pro/bin/thisroot.sh ]; then
    source ${topd}/root/pro/bin/thisroot.sh
elif [ -e %%INSTALLDIR%%/bin/thisroot.sh ]; then
    source %%INSTALLDIR%%/bin/thisroot.sh
fi
"""
root.postwithenv={"Centos6" : ["pip install rootpy"]}
root.postwithenv["Centos7"]=root.postwithenv["Centos6"]
root.postwithenv["Ubuntu"]=root.postwithenv["Centos6"]

#######################  KETTLE  ############################
class Kettle(Component):
    def script(self):
        dest = "kettle.zip"
        self.copy(self.src_from, dest)
        self.run("unzip -o -q " + dest)
        #default to our hadoop version
        f = open("data-integration/plugins/pentaho-big-data-plugin/plugin.properties")
        lines = f.read()
        f.close()
        f = open("data-integration/plugins/pentaho-big-data-plugin/plugin.properties", "w")
        f.write(lines.replace("active.hadoop.configuration=hadoop-20", "active.hadoop.configuration=cdh47"))
        f.close()
        #default to not show the welcome screen
        addition = """

        #KPMG: workaround for crashing loading screen on Centos!
        dir=$HOME
        if [ -z "$KETTLE_HOME" ]; then
          dir=$HOME/.kettle/
        else
          dir=$KETTLE_HOME
        fi
        if [ -e "$dir/.spoonrc" ]; then
          #OK, do nothing since you already created the file
          dir=$dir
        elif [ -e "$dir" ]; then
          echo "ShowWelcomePageOnStartup=N" > "$dir"/.spoonrc
        else
          mkdir $dir
          echo "ShowWelcomePageOnStartup=N" > "$dir"/.spoonrc
        fi

"""
        f = open("data-integration/spoon.sh")
        lines = f.readlines()
        #fix bug PDI-9977, http://jira.pentaho.com/browse/PDI-9977
        lines = [line.replace("LIBPATH=$BASEDIR/", "LIBPATH=") for line in lines if "cd -" not in line]
        f.close()
        f = open("data-integration/spoon.sh", "w")
        f.write(lines[0])
        f.write(addition)
        f.write('\n'.join(lines[1:]))
        f.close()
        self.run("mv data-integration " + self.installDir)
        return


kettle = Kettle("Kettle")
kettle.doInstall = True
kettle.installSubDir = "kettle"
kettle.src_from = [li.fromKPMGrepo("pdi-ce-5.2.0.0-209.zip", arch="noarch"),
                   "http://downloads.sourceforge.net/project/pentaho/Data%20Integration/5.2/pdi-ce-5.2.0.0-209.zip?r"
                   "=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fpentaho%2Ffiles%2FData%2520Integration%2F5.2%2Fpdi-ce"
                   "-5.2.0.0-209.zip%2Fdownload&ts=1415797032&use_mirror=netcologne"]
kettle.node = False
kettle.workstation = True
kettle.pre = {"Centos6": ["yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel"],
              "Centos7": ["yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel"],
              "Ubuntu": ["apt-get -y install default-jre default-jdk "]
              }
kettle.registerToolbox(toolbox)
kettle.env = """
ket="%%INSTALLDIR%%"
if [ -d ${ket}  ]; then
    if [[ ":$PATH:" == *":$ket:"* ]]; then
        true
    else
        export PATH=${ket}:${PATH}
    fi
fi
"""

#######################  R  ############################
class RComponent(Component):
    def script(self):
        return True


r = RComponent("R")
r.doInstall = True
r.pre = {"Centos6": ["rpm -Uvh " + li.fromKPMGrepo("epel-release-6-8.noarch.rpm", arch="centos6"),
                     'yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                     #http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm",
                     "yum -y install readline-devel",
                     "yum -y install R",
                     "yum -y install R-* --skip-broken"  #not everything installs on Centos6!
                     ],
         "Centos7": ["rpm -Uvh " + li.fromKPMGrepo("epel-release-7-5.noarch.rpm", arch="centos7"),
                     'yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                     #http://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm ",
                     "yum -y install readline-devel",
                     "yum -y install R",
                     "yum -y install R-* --skip-broken"  #skip broken, just in case ...
                     ],
         "Ubuntu": ["apt-get -y install libreadline6 libreadline6-dev libc6-dev-i386",
                    "apt-get -y install build-essential g++",
                    "apt-get -y install r-base-dev",
                    "apt-get -y install python-rpy2"
                    ]
         }
r.postwithenv={"Centos6":["conda update conda --yes; pip install rpy2"]}
r.postwithenv["Centos7"]=r.postwithenv["Centos6"]
r.postwithenv["Ubuntu"]=["conda update conda --yes; conda install -c asmeurer rpy2 --yes"]
r.registerToolbox(toolbox)