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

We don't recommend you to edit this file. Instead we suggest to create/add configurations to /etc/kave/CustomInstall.py

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
        guess_installed = self.installDirVersion + os.sep + "scripts" + os.sep + "KaveEnv.sh"
        if os.path.exists(guess_installed):
            return guess_installed+" "+self.version
        installfrom = self.installfrom()
        return installfrom + os.sep + "scripts" + os.sep + "KaveEnv.sh"

    def buildEnv(self):
        prepend = False
        rest = []
        scriptloc = self.envscript().split()[0]
        #recreate env script in case it totally does not exist, or somehow is missing the intro...
        if not os.path.exists(scriptloc) and os.path.exists(self.installDirVersion + '/scripts/'):
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

            ) + "/ " + self.installDirVersion)
        #self.run("mv ./"+self.installfrom().rstrip('/').split('/')[-1]+" "+self.installDir)
        f = open(self.installfrom() + os.sep + "scripts" + os.sep + "autoKaveEnv.sh")
        l = f.read()
        f.close()
        l = l.replace("%ENVSCRIPT%", self.installDirPro+'/scripts/KaveEnv.sh')
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
            if linuxVersion.lower().startswith("centos6"):
                self.run('gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string '
                         +'--set /desktop/gnome/background/picture_filename '+self.installDirPro+'/figs/KAVE_wp'+str(self.wallpaperselect)+'.png')
                self.run('gconftool-2 --direct --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults --type string '
                         +' --set /desktop/gnome/background/picture_options centered')
            else:
                cfpath='/etc/xdg/xfce4/xfconf/xfce-perchannel-xml'
                template='xfce4-desktop.xml'
                if linuxVersion.lower().startswith("centos7"):
                    cfpath='/etc/dconf/db/local.d'
                    template='00-background'
                if not os.path.exists(cfpath):
                    os.makedirs(cfpath,0755)
                self.run('cp -f '+os.path.join(os.path.dirname(os.path.realpath(__file__)),template)+ ' ' + cfpath)
                self.run('sed -i "s/%%INSTALLDIRPRO%%/'+self.installDirPro.replace('/','\\/')+'/g"  '+ os.path.join(cfpath,template))
                self.run('sed -i "s/%%WPNUM%%/'+str(self.wallpaperselect)+'/g"  '+os.path.join(cfpath,template))
                if linuxVersion.lower().startswith("centos7"):
                    self.run('dconf update')
        return True


toolbox = Toolbox("KaveToolbox")
toolbox.doInstall = True
toolbox.installSubDir = "KaveToolbox"
toolbox.freespace = 100
toolbox.usrspace = 200
toolbox.tempspace = 100
toolbox.workstationExtras = {"Centos6": ['yum -y groupinstall "Desktop" "Desktop Platform" "X Window System" "Fonts" --exclude=NetworkManager\\*',# --exclude=pulseaudio\\* --skip-broken',
                                         'yum -y install tigervnc-server firefox xpdf'],
                             "Centos7": ['yum -y groupinstall "Desktop"  "GNOME Desktop" "Desktop Platform" "X Window System" "Fonts"',#  --exclude=NetworkManager\\* --exclude=pulseaudio\\* --skip-broken',
                                         'yum -y install tigervnc-server firefox pixman pixman-devel libXfont xpdf'],
                             "Ubuntu": ['apt-get -y install firefox xpdf',
                                        'if dpkg -l xserver-xorg-input-mouse 2>/dev/null > /dev/null ; then true; else '# Only install x if x not installed
                                        +'apt-get -y install xfce4 xfce4-goodies;'
                                        +'fi;',
                                        'apt-get -y install tightvncserver'
                                        ]
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

ktbv='%%VERSION%%'
pro='yes'

# Choose the versioning to use
# No arguments -- use all pro versioning
# X : use fixed versioning from version X install

if [ -n "$1" ]; then
   if [ ${ktbv} == "$1" ]; then
     pro='no'
   elif [ "$1" == 'pro' ]; then
     pro='yes'
   elif [ -d %%INSTALLDIR%%/${1} ]; then
     source %%INSTALLDIR%%/${1}/scripts/KaveEnv.sh $1
     exit 0
   fi
fi

if [ ${pro} == 'yes' ]; then
    export KAVETOOLBOX=%%INSTALLDIRPRO%%
else
    export KAVETOOLBOX=%%INSTALLDIRVERSION%%
fi

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
        if [ -e ${KAVETOOLBOX}/Welcome.banner ]; then
            cat ${KAVETOOLBOX}/Welcome.banner
        fi
    fi
fi


#only add directories to path if they are not already there!
if [[ ":$PATH:" == *":$KAVETOOLBOX/bin:$KAVETOOLBOX/scripts:"* ]]; then
    true
else
    export PATH=$KAVETOOLBOX"/bin:"$KAVETOOLBOX"/scripts:"${PATH}
fi

if [[ ":$PYTHONPATH:" == *":$KAVETOOLBOX/python:"* ]]; then
    true
else
    export PYTHONPATH=$KAVETOOLBOX"/python:"${PYTHONPATH}
fi

#Add spark if spark is installed
if type pyspark >/dev/null 2>/dev/null; then
  export SPARK_HOME=`readlink -f \`which pyspark\``
  export SPARK_HOME=`dirname \`dirname $SPARK_HOME\``
  if [[ ":$PYTHONPATH:" == *":$SPARK_HOME/python:"* ]]; then
    true
  else
    export PYTHONPATH=${SPARK_HOME}"/python:"${PYTHONPATH}
  fi
fi

"""

java = Component("java")
java.version = '1.8'
java.usrspace = 175
java.pre = {"Centos6": ["yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel"],
            "Centos7": ["yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel"],
            "Ubuntu" : ["add-apt-repository ppa:openjdk-r/ppa -y",
                        "apt-get update",
                        "apt-get -y install openjdk-8-jre openjdk-8-jdk openjdk-8-source "]
            }
java.post = {"Centos6": ["bash -c 'IFS=\";\" read -r jdir string <<< `ls -dt /usr/lib/jvm/java-1.8*-openjdk*`; export jdir; "
                         "alternatives --install /usr/bin/java java ${jdir}/jre/bin/java 20000; "
                         "if [ -e ${jdir}/bin/javac ]; then alternatives --install /usr/bin/javac javac ${jdir}/bin/javac 20000; fi ;"
                         "if [ -e ${jdir}/jre/bin/javaws ]; then alternatives --install /usr/bin/javaws javaws ${jdir}/jre/bin/javaws 20000; fi; "
                         "alternatives --set java ${jdir}/jre/bin/java; "
                         "if [ -e ${jdir}/bin/javac ]; then alternatives --set javac ${jdir}/bin/javac; fi; "
                         "if [ -e ${jdir}/jre/bin/javaws ]; then alternatives --set javaws ${jdir}/jre/bin/javaws; fi; '"
                         ]
             }
java.post["Centos7"] = java.post["Centos6"]
java.post["Ubuntu"] = [c.replace("alternatives","update-alternatives") for c in java.post["Centos6"]]

#######################  ECLIPSE  ############################

class EclipseComponent(Component):
    """
    Subclass to install eclipse
    """

    def script(self):
        dest = "myeclipse.tar.gz"
        self.copy(self.src_from, dest)
        self.run("tar xzf " + dest)
        if os.path.exists("eclipse"):
            os.system("mv eclipse " + self.installDirVersion)
        elif os.path.exists("opt/eclipse"):
            os.system("mv opt/eclipse " + self.installDirVersion)
        else:
            self.bauk("couldn't find eclipse directory to move!")
        if linuxVersion == "Centos6":
            self.run("echo '-Dorg.eclipse.swt.internal.gtk.cairoGraphics=false' >> " + self.installDir + "/eclipse.ini")
        return


eclipse = EclipseComponent("Eclipse")
eclipse.workstation = True
eclipse.node = False
eclipse.children = {"Centos6" : [java],
                    "Centos7" : [java],
                    "Ubuntu" : [java]}
eclipse.installSubDir = "eclipse"
eclipse.version = "1.3"
eclipse.src_from = li.fromKPMGrepo("eclipse.tar.gz", arch="noarch")
eclipse.freespace = 500
eclipse.usrspace = 150
eclipse.tempspace = 1000
eclipse.registerToolbox(toolbox)
eclipse.env = """
ecl="%%INSTALLDIRVERSION%%"
if [ ${pro} == 'yes' ]; then
  ecl="%%INSTALLDIRPRO%%"
fi

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
        self.run(dest + " -b -p " + self.installDirVersion)
        self.buildEnv()

conda = Conda(cname="anaconda")
conda.pre={"Centos6":['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                      'yum -y install epel-release',
                      'yum -y install libffi* cyrus-sasl* geos*']}
conda.pre["Centos7"]=conda.pre["Centos6"]
conda.pre["Ubuntu"]=["apt-get -y install build-essential g++ libffi* libsasl2-dev libsasl2-modules-gssapi-mit* cyrus-sasl2-mit* libgeos-dev"]
conda.postwithenv={"Centos6" : ["conda update conda --yes","conda install pip --yes",
                                "pip install delorean seaborn pygal mpld3 ",
                                "pip install cairosvg pyhs2 shapely descartes",
                                "pip install pyproj folium vincent pam",
                                "pip install py4j",
                                "pip install pymongo",
                                "if type krb5-config 2>&1 > /dev/null; then pip install pykerberos; fi",
                                " if [  ! -z \"$ROOTSYS\" ] ; then pip install rootpy ; pip install root_numpy;"
                                + " pip install git+https://github.com/ibab/root_pandas; fi "]}
conda.postwithenv["Centos7"]=conda.postwithenv["Centos6"]
conda.postwithenv["Ubuntu"]=conda.postwithenv["Centos6"]
conda.doInstall = True
conda.freespace = 1500
conda.usrspace = 300
conda.tempspace = 300
conda.installSubDir = "anaconda"
conda.version = "2.4.1"
conda.registerToolbox(toolbox)
conda.src_from = [{"arch":"noarch","suffix":"-Linux-x86_64.sh"},
                  "https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.4.1-Linux-x86_64.sh"]
conda.env = """
ana="%%INSTALLDIRVERSION%%"
if [ ${pro} == 'yes' ]; then
  ana="%%INSTALLDIRPRO%%"
fi
if [ -d ${ana}  ]; then
    if [[ ":$PATH:" == *":$ana/bin:"* ]]; then
        true
    else
        export PATH=${ana}/bin:${PATH}
    fi
fi
"""

#######################  pygsl  ############################
gsl = Component("pygsl")
gsl.doInstall = True
gsl.version = "2.1.1"
gsl.src_from=[{"arch":"noarch","suffix":".tar.gz"},
              "http://downloads.sourceforge.net/project/pygsl/pygsl/pygsl-2.1.1/pygsl-2.1.1.tar.gz"]
gsl.pre = {"Centos6": ["yum -y install gsl gsl-devel"]}
gsl.pre["Centos7"]=gsl.pre["Centos6"]
gsl.pre["Ubuntu"]=["apt-get -y install build-essential g++ libgsl0-dev gsl-bin"]
gsl.prewithenv["Centos6"]=[' isinst=`python -c "import pkgutil; print pkgutil.find_loader(\\"numpy\\") is not None;"`;'
                          ' if [ ${isinst} == "False" ]; then echo "no scipy/numpy installed, so will not install pygsl,'
                          ' turn on the anaconda installation! (was it skipped?) or turn off pygsl." ; exit 1 ; fi ']
gsl.prewithenv["Centos7"]=gsl.prewithenv["Centos6"]
gsl.prewithenv["Ubuntu"]=gsl.prewithenv["Centos6"]

gsl.postwithenv={"Centos6":[' isinst=`python -c "import pkgutil; print pkgutil.find_loader(\\"pygsl\\") is not None;"`;'
                            ' if [ ${isinst} == "False" ]; then cd pygsl-2.1.1; python setup.py build; python setup.py install ; fi ']
                 }
gsl.postwithenv["Centos7"]=gsl.postwithenv["Centos6"]
gsl.postwithenv["Ubuntu"]=gsl.postwithenv["Centos6"]
gsl.usrspace = 3
gsl.tempspace = 2
gsl.registerToolbox(toolbox)

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
               "easy_install": [], #"-z dumbo"], # dumbo is broken at the moment via easy_install
               "JavaHome": None,
               "HadoopHome": None
               }
hpy.pre = {"Centos6": ["yum -y install boost boost-devel openssl-devel"],
           "Centos7": ["yum -y install boost boost-devel openssl-devel"],
           "Ubuntu": ["apt-get -y install libboost-python-dev libssl-dev"]
           }
hpy.registerToolbox(toolbox)

#######################  ROOT  ############################

# Ubuntu fix libpng
libpng=Component("libpng")
libpng.version="1.5.22"
libpng.doInstall = True
libpng.src_from={"suffix":".tar.gz"}
libpng.post={"Ubuntu" : ["bash -c 'if [ ! -e /usr/local/libpng ]; then cd libpng-1.5.22; ./configure --prefix=/usr/local/libpng; make; make install;"
                         + " ln -s /usr/local/libpng/lib/libpng15.so.15 /usr/lib/libpng15.so.15; fi;'"]}

# Centos6 Glew Fix
glew=Component("glew")
glew.doInstall = True
glew.version="1.5.5-1"
glew.src_from={"suffix":".el6.x86_64.rpm"}

# Centos6 GlewDev Fix
glewdev=Component("glew-devel")
glewdev.doInstall = True
glewdev.version="1.5.5-1"
glewdev.src_from={"suffix":".el6.x86_64.rpm"}

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


    def script(self):
        for ap in sys.path:
            if conda.installSubDir in ap:
                self.bauk(
                    "Cannot compile ROOT because you have already inserted anaconda onto your python path. Please "
                    "touch ~/.nokaveEnv, begin a new shell, and try again")
        #if not test:
        arch_url = li.fromKPMGrepo("root_" + self.version + "_" + linuxVersion.lower() + ".tar.gz")
        noarch_url = li.fromKPMGrepo("root_" + self.version + "_noarch.tar.gz", arch="noarch")
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
        self.run("tar xzf " + dest)
        os.system("mkdir -p " + os.sep.join(self.installDirVersion.split(os.sep)[:-1]))
        os.system("mv root " + self.installDirVersion)
        os.chdir(self.installDirVersion)
        if self.options["Strategy"] == "Compile":
            self.compile()
            os.chdir(self.tmpdir)
        os.chdir(self.tmpdir)
        for package in self.options["pip"]:
            self.run(
                "bash -c 'source " + self.toolbox.envscript() + ";"
                + " source " + self.installDirVersion + "/bin/thisroot.sh;"
                + " pip install " + package + "'"
                )
        return


root = RootComponent("root")
root.doInstall = True
root.installSubDir = "root"
root.version = "v5.34.34"
root.options = {"Strategy": "Default",
                "LowMemoryMode": False,
                "conf": {
                    "Centos7": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                               "--enable-mathmore --fail-on-missing",
                    "Centos6": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit  "
                               "--enable-mathmore --fail-on-missing",
                    "Ubuntu": "linuxx8664gcc --enable-python --enable-minuit2 --enable-roofit --enable-cxx11 "
                              "--enable-mathmore --fail-on-missing"},
                "pip": ["root_numpy", "git+https://github.com/ibab/root_pandas", "rootpy"]
                }
root.src_from = "ftp://root.cern.ch/root/"
root.pre = {"Centos7": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Centos6": ['yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                        "wget http://public-yum.oracle.com/RPM-GPG-KEY-oracle-ol6",
                        "rpm --import RPM-GPG-KEY-oracle-ol6",
                        "yum -y install libX11-devel libXpm-devel libXft-devel libXext-devel fftw-devel mysql-devel "
                        "libxml2-devel ftgl-devel libglew glew glew-devel qt qt-devel gsl gsl-devel"
                        ],
            "Ubuntu": [
                "apt-get -y install x11-common libx11-6 x11-utils libX11-dev libgsl0-dev gsl-bin libxpm-dev "
                "libxft-dev g++ gfortran build-essential g++ libjpeg-turbo8-dev libjpeg8-dev libjpeg8-dev libjpeg-dev "
                " libtiff5-dev libxml2-dev libssl-dev libgnutls-dev libgmp3-dev libpng12-dev libldap2-dev libkrb5-dev "
                "freeglut3-dev libfftw3-dev python-dev libmysqlclient-dev libgif-dev libiodbc2 libiodbc2-dev "
                "libxext-dev libxmu-dev libimlib2 gccxml libxml2 libglew-dev glew-utils libc6-dev-i386"
                ]
            }
root.children = { "Centos6" : [glew, glewdev],
                 "Centos7" : [],
                 "Ubuntu" : [libpng]
                 }
root.registerToolbox(toolbox)
root.freespace = 750
root.usrspace = 300
root.tempspace = 500
root.env = """
#enable the most recent root installation
rt="%%INSTALLDIRVERSION%%"
if [ ${pro} == 'yes' ]; then
  rt="%%INSTALLDIRPRO%%"
fi
if [ -e "$rt"/bin/thisroot.sh ]; then
    source "$rt"/bin/thisroot.sh
fi
"""

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
        f.write(lines.replace("active.hadoop.configuration=hadoop-20", "active.hadoop.configuration=hdp22"))
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
        self.run("mv data-integration " + self.installDirVersion)
        return


kettle = Kettle("Kettle")
kettle.doInstall = True
kettle.freespace = 700
kettle.usrspace = 130
kettle.tempspace = 1200
kettle.version = "5.4.0.1-130"
kettle.installSubDir = "kettle"
kettle.src_from = [{'filename':"pdi-ce", 'suffix':".zip", 'arch':"noarch"},
                   "http://downloads.sourceforge.net/project/pentaho/Data%20Integration/5.4/pdi-ce-5.4.0.1-130.zip?r"
                   "=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fpentaho%2Ffiles%2FData%2520Integration%2F5.4%2F&ts=1460476499&use_mirror=tenet"
                   ]
kettle.node = False
kettle.workstation = True
kettle.pre = {"Centos6": ["yum -y install webkitgtk"],
              "Centos7": ["yum -y install webkitgtk"],
              "Ubuntu": ["apt-get -y install libwebkitgtk-dev"]
              }
kettle.children = {"Centos6" : [java],
                   "Centos7" : [java],
                   "Ubuntu" : [java]}
kettle.registerToolbox(toolbox)
kettle.env = """
ket="%%INSTALLDIRVERSION%%"
if [ ${pro} == 'yes' ]; then
  ket="%%INSTALLDIRPRO%%"
fi
if [ -d ${ket}  ]; then
    if [[ ":$PATH:" == *":$ket:"* ]]; then
        true
    else
        export PATH=${ket}:${PATH}
    fi
fi
"""

#######################  robomongo  ############################
robo = Component("robomongo")
robo.doInstall = False # Don't install at the moment by default, because it doesn't work with mongo 3.0
robo.node = False
robo.workstation = False
robo.version = "0.8.4"
robo.src_from=[{"suffix":".tar.gz"}]
robo.pre = {"Centos6": ["yum install -y glibc.i686 libstdc++.i686 libgcc.i686"]}
robo.pre["Centos7"]=robo.pre["Centos6"]
robo.pre["Ubuntu"]=["apt-get -y install libxcb-icccm4 libxkbcommon-x11-0 libxcb-xkb1 libxcb-render-util0 libxcb-keysyms1 libxcb-image0"]
robo.post = {"Centos6": ["yum -y install robomongo-*.rpm"]}
robo.post["Centos7"]=robo.post["Centos6"]
robo.post["Ubuntu"]=["dpkg -i robomongo-*.deb"]
robo.usrspace = 40
robo.tempspace = 20
robo.registerToolbox(toolbox)

#######################  R  ############################
class RComponent(Component):
    def script(self):
        return True


r = RComponent("R")
r.doInstall = True
r.pre = {"Centos6": ['yum -y install epel-release',
                     #"rpm -Uvh " + li.fromKPMGrepo("epel-release-6-8.noarch.rpm", arch="centos6"),
                     'yum -y groupinstall "Development Tools" "Development Libraries" "Additional Development"',
                     #http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm",
                     "yum -y install readline-devel",
                     "yum -y install R",
                     "yum -y install R-* --skip-broken"  #not everything installs on Centos6!
                     ],
         "Ubuntu": ["apt-get -y install libreadline6 libreadline6-dev libc6-dev-i386",
                    "apt-get -y install build-essential g++",
                    "apt-get -y install r-base-dev",
                    "apt-get -y install python-rpy2"
                    ]
         }
r.pre["Centos7"]=r.pre["Centos6"]
r.postwithenv={"Centos6":["conda update conda --yes; pip install rpy2"]}
r.postwithenv["Centos7"]=r.postwithenv["Centos6"]
r.postwithenv["Ubuntu"]=["conda update conda --yes; conda install -c asmeurer rpy2 --yes"]
r.usrspace = 150
r.tempspace = 1
r.registerToolbox(toolbox)