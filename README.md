KaveToolbox
===========

Data analytics toolkit part of the KAVE, installed with [AmbariKave](http://github.com/KaveIO/AmbariKave), and also installable stand-alone http://beta.kave.io, a wiki for the entire KAVE is maintained on the cluster installer, [AmbariKave wiki](http://github.com/KaveIO/AmbariKave/wiki)


Installing more modules on top of kave toolbox as the root user:
----------------------------------------------------------------

Examples:

* Installing a python module into anaconda when the first install used root privilages
* Installing some derived library (some ROOT component) which needs ROOT and python integration

Why is this complicated?

* The root user by default does not have the KAVE environment setup, it has the system python and cannot see the kave components
* whatever new modules you try and install as root will then build against the system libraries, not KaveToolbox

What errors might I see?

* Complaints that you don't have the right privilages
* Software you think you've installed does not link or run correctly against KaveToolbox
* Software you think you've installed does not run for your user, but seems to run for the root user

Fix:

* sudo su #changes you to the root user
* source /opt/KaveToolbox/pro/scripts/KaveEnv.sh # the regular kave environment is not automatically fired for the root user
* #install as normal

Example:

```
sudo su
source /opt/KaveToolbox/pro/scripts/KaveEnv.sh
conda update conda
pip install pymongo
```

Contents:
---------

Our libraries:

* RootNotes: using ROOT plotting in ipython notebooks
* StatTools: tool for confidence level calculations
* LogMon   : monitor a logfile (e.g. hive logfile)
* gdown    : Auto download files from google docs/drive
* geomaps  : Utilities to give a postal code-based map, or other geographical-based map in ipython Notebook

Installer for:

* Python through (ana)conda, includes SciPy, numpy, pip etc., (continuum.io)
* ROOT, CERN's data analysis package (root.cern.ch)
* Pentaho kettle, graphical process and data management tool (http://community.pentaho.com/projects/data-integration/)
* R with integration into iPython notebook (http://nbviewer.ipython.org/github/dboyliao/cookbook-code/blob/master/notebooks/chapter07_stats/08_r.ipynb)
* Additional hadoopy-python modules, dumbo, mrjob, pyleus and pymongo_hadoop (if hadoop is available)
* robomongo (only if specifically configured, see ReleaseNotes.md for details)

Examples of:

* IPython notebooks for RootNotes, StatTools, R and geomaps

Supported Systems:
----------------

CentOS6, CentOS7 and Ubuntu 14 are used for testing, although no guarantees are given.

Only bash as a default shell is supported at the moment, users with a different default have reported many problems.


Introduction:
---------

KaveToolbox is aimed at making the installation of our key analytics software and libraries seamless so that one-click deployment is possible and encouraged, taking the pain out of working out prerequisites, compilation, for most of our software. When you just want to get stuck straight into the data, you can bring along your same toolbox. It ensures a common environment to allow for simpler code distribution across all data nodes "fire and forget" instead of "push and pray".

KaveToolbox recognises two types of distribution:

* Node - no x-windows, needs libraries necessary for linking/running jobs, but no GUI management for that
* Workstation - complete data analysis workstation, with all graphical components, vnc, x-windows, etc.


Minimum Requirements:
---------------------

* Node: 2.5 GB of disk space for the software, additional 3 GB temp space needed during installation
* Workstation: 4 GB of disk space for the software, additional 3 GB temp space needed during installation

* Node: 1 core 2GB of RAM
* Workstation: 2 core 4GB RAM

* An internet connection (many packages will be downloaded form various sites)
* Centos6/7 review your yum.conf file to make sure you are not ignoring certain packages from being installed

Nodes are likely to have even higher requirements for other service requirements such as Hadoop or storm.

Recommended workstation:
-----------------------

* (2 core + 4 GB RAM)+(1 core + 2 GB RAM)*(number of simultaneous users)
* (100 GB)*(number of all-time users) home directory
* 20 GB "/" free on top of system size, or direct mount of 20 GB as /opt/
* 100 GB "/tmp" size
* GB Ethernet with high upload bandwidth for VNC connections
* We recommend that any servers/services requiring 100% uptime are not run on the analysis workstation (e.g. Hue/Ganglia/nagios/ldap) since analysis users will have erratic usage with a very high peak usage, we recommend running such services on dedicated servers in the network.

Installation:
-------------

You have two choices:

1. Installing a released version from the repos server
2. Installing the head, branch or specific tag from GIT

We recommend to install with the default configurations, but in case you want to modify the configurations you can create a file in /etc/kave/CustomInstall.py,For an example and more information run the installer with --help

* 1: Installing the released version, for example, 2.1-Beta-Pre

```
yum -y install wget curl tar zip unzip gzip
wget http://repos:kaverepos@repos.kave.io/noarch/KaveToolbox/2.1-Beta-Pre/kavetoolbox-installer-2.1-Beta-Pre.sh
sudo bash kavetoolbox-installer-2.1-Beta-Pre.sh [--quiet]
```
(--quiet is for a quieter install, remove the brackets!)
Remember the help at this stage  [--help]

( NB: the repository server uses a semi-private password only as a means of avoiding robots and reducing DOS attacks
  this password is intended to be widely known and is used here as an extension of the URL )

* 2: Installing the head from git, Example given using ssh.

```
#test ssh keys with
ssh -T git@github.com
#if this works,
git clone git@github.com:KaveIO/KaveToolbox.git
#then install with
sudo ./KaveToolbox/scripts/KaveInstall [--quiet]
```
(--quiet is for a quieter install, remove the brackets!)
Remember the help at this stage [--help]


* Then to browse through examples

```
cd /opt/KaveToolbox/pro/examples
ipython notebook
```
And/or visit http://nbviewer.ipython.org/

* Optional: Editing configuration files
  * Default will install into directories in /opt
  * Default will not overwrite existing packages
  * Default configurations are well-tested, read all the configurations from config/kavedefaults.py
  * To override configurations, create a simple python file in /etc/kave/CustomInstall.py
  * this python should be used to logically overwrite any property of a service appearing in kavedefaults.py and will not be over-written on re-install/upgrade
  * For an example and more information call ./kavetoolbox/scripts/KaveInstall --help

* Optional: Set mirrors/nearside cache
  * A list of mirrors of where to locate our software can be added to /etc/kave/mirror .
  * The "mirror" file will be interpreted line-by-line should be used to add a list of nearside cache directories or nearside mirrors of the KPMG repository.
  * All mirrors listed here must follow the same directory structure as the main repository, this looks like: **mirror/os-version(s)/KaveToolbox/toolbox-version(s)/files.ext**
  * See more details below in setting up such a cache

* Optional: Additional installation options
  * The installer script has more options to help steer the installation
  * take a look at the --help for the KaveInstall script for more details.
  * Examples include automatically cleaning old versions from /opt. (--clean-after)
  * Examples include completely cleaning directories before install from /opt (--clean-before)


Troubleshooting:

* "Warning: end of file not at end of line" during installation: this means you don't have enough virtual memory for the compilation of root. Modify configuration file for "low memory mode"
* Other errors in root or python installation: if installation fails, it may be due to conflicts with a previous install, try touch ~/.nokaveEnv and then obtain a clean shell, possibly via ssh


Post-installation:
------------------

* **ProtectNotebooks.sh script:** if run as root, will add a system-wide ipython\_notebook\_config.py file
                              if run as a user will add a user-level ipython\_notebook\_config.py file
                              this file chooses a default port based on username and protects notebooks with the user's login password

Re-installing:
--------------

* Re-running the installer over a pre-existing installation will only install new software and pick up new configuration changes.
* New software will be installed into versioned directories, to make it easier to track
* In case of an error during installation the install will stop, to complete an incomplete installation, re-run the installer,
* To fix some component within a broken installation, delete any installed directories in /opt (or whatever you specified them to be) and re-run the installer, it will only install those parts you either deleted or didn't work the first time.
* To perform a complete re-install remove relevent directories from /opt, like /opt/root, /opt/kettle etc. or add the --clean-before flag to the script
* To re-install only the core KaveToolbox with any new features, see Updating


Updating:
---------

There are three possible update mechanisms

* Downloading/rerunning the latest install script (from git or from the repository)
* Running the KaveUpdate script

```
sudo /opt/KaveToolbox/pro/scripts/KaveUpdate --list
sudo /opt/KaveToolbox/pro/scripts/KaveUpdate --help
sudo /opt/KaveToolbox/pro/scripts/KaveUpdate --quiet
```

The update script works well for updating 2.X versions, and can also be used for 1.X, but only with the --clean-before flag.
The --clean-after flag is a common addition to the update to remove deprecated software after install

Usage
-----

* The correct paths to directly use our tools will be automatically added to your environment provided:
   1. you are not the root user
   2. you do not have .nokaveEnv in your home directory
   3. you use bash as your default shell

* In other cases you will need to get/set environment manually

  source [directory, e.g. /opt/KaveToolbox/pro/scripts]/KaveEnv.sh

* the ASCII-art KAVE banner only shows up for interactive, non-dumb terminals, to turn off the KAVE banner even in that case do

  touch ~/.nokaveBanner

* To disable automatic setting of the environment for this user:

  touch ~/.nokaveEnv

* To force setting the environment for this user in case they would normally be skipped, first remove .nokaveEnv, then:

  touch ~/.kaveEnv

Test if it works?
-----------------

* take a look at the examples!

```
  cd $KAVETOOLBOX/examples
  ipython notebook
  --> Choose, for example, rootnotes.ipynb
  --> Kernel --> Restart
  --> Cells --> RunAll
```

Coming Soon
-----------

No additional plans on the horizon

Internet during installation, firewalls and nearside cache/mirror options
-------------------------------------------------------------------------

Ideally all of your nodes will have access to the internet during installation in order to download software.

If this is not the case, you can, possibly, implement a near-side cache/mirror of all required software. This is not very easy, but once it is done one time, you can keep it for later.
* Centos6: [Howto](https://ostechnix.wordpress.com/2013/01/05/setup-local-yum-server-in-centos-6-x-rhel-6-x-scientific-linux-6-x/)
* EPEL: [Mirror FAQ](http://www.cyberciti.biz/faq/fedora-sl-centos-redhat6-enable-epel-repo/) , [Mirroring](https://fedoraproject.org/wiki/Infrastructure/Mirroring)
* Ambari: [Local Repositories](https://ambari.apache.org/1.2.1/installing-hadoop-using-ambari/content/ambari-chap1-6.html)  [Deploying HDP behind a firewall](http://docs.hortonworks.com/HDPDocuments/HDP1/HDP-1.2.1/bk_reference/content/reference_chap4.html)

To setup a local near-side cache for the KAVE tool stack is quite easy.
First either copy the entire repository website to your own internal apache server, or copy the contents of the directories to your own shared directory visible from every node.

```
mkdir -p /my/shared/dir
cd  /my/shared/dir
wget -R http://repos:kaverepos@repos.kave.io/
```

Then create a /etc/kave/mirror file on each node with the new top-level directory to try first before looking for our website:
```
echo "/my/shared/dir" >> /etc/kave/mirror
echo "http://my/local/apache/mirror" >> /etc/kave/mirror
```

So long as the directory structure of the nearside cache is identical to our website, you can drop, remove or replace, any local packages you will never install from this directory structure, and update it as our repo server updates.

FAQ:
------


## How can I install from behind a proxy?

You might consider creating a near-side cache, and/or configuring your proxy settings correctly, since we use wget for the downloads, your existing proxy settings (e.g. HTTP_PROXY environment variable) should be sufficient.

Don't forget that the root user/sudo also must comminicate over the proxy, and this may mean propagating the right environment variables. Try adding:
```
Defaults env_keep +="http_proxy"
Defaults env_keep +="https_proxy"
```
to your sudoers file with visudo

from [here](http://stackoverflow.com/questions/8633461/how-to-keep-environment-variables-when-using-sudo)

## I can reach the repos server fine, but the installer still tells me there is a problem!

We can't trouble shoot your networking issues for you, but if you are trying to install from behind a proxy, check the "How can I install behind a proxy" FAQ, also talk with your network administrator and decide if you need to setup a nearside cache.

## The precompiled root version will not run from a non-default configuration

* This is to be expected.
* If you have edited the configuration file to change installed packages or locations, it is quite likely that root will not install from the precompiled version correctly.
* To fix this, revert your copy of kaveconfiguration.py to the default settings and re-install root, or, configure/compile root yourself in this new location like:

```
cd /root/install/location
./configure [options e.g. linuxx8664gcc --enable-python --enable-mathmore --enable-minuit2 --enable-roofit --fail-on-missing]
make -j numcores
```

or follow the instructions on the root website to install root yourself

## ROOT installation fails during yum install

Many different packages are needed, did you maybe run out of space? Or did you ignore kernel packages in your yum.conf?

Check /etc/yum.conf and see if there is anything your are ignoring or forbidding from installing.

## can't checkout due to gnome-ssh-askpass Gtk-WARNING cannot open display

This is gnome trying to spawn an x window to have you enter your password. Work around by:

unset SSH_ASKPASS

## (Developer) How to add a new precompiled root version

1. Install KaveToolbox with anaconda and that root version onto one a machine running a supported OS
2. cp -r /opt/root/version /some/temp/dir/root
3. cd /some/temp/dir
4. tar cvzf root\_version\_os.tar.gz root
5. Upload tar to the repo server into the correct directory

## Is it possible to install the software without root/superuser privilages?

So long as the pre-requisites are already installed (see the yum install commands in the kaveconfiguration.py) it is possible to install all the software we package into a local directory, however that is not implemented yet and will not permit seamless integration of all users and machines in a network, and it will not be possible to automatically source the environment for all users.

## Javascript elements of d3js, geomaps, or vincent will not display

This is usually your local browser which is blocking things:

* Not allowed to run unsafe/unverified scripts (look for the tell-tale icon in the browser toolbar)
* Not allowed to display mixed content (if the trying to display https, look for the tell-tale icon in the browser toolbar)

In the first case, you can simply permit scripts running, by clicking on the correct icon and choosing the correct option.

In the second case, there are tow solutions. Best is to restart/modify mpld3 options with the correct options to switch to https for the javascript part aswell. The other option is to allow mixed content in your browser for ipython notebooks.

http://stackoverflow.com/questions/21089935/unable-plot-with-vincent-in-ipython
https://mpld3.github.io/modules/API.html
https://mpld3.github.io/modules/API.html#mpld3.enable_notebook

## VNC opens to a black screen with just a small dialog box?

On Centos7, for some reason the vnc installation/start does not be default recognise the gnome installation

To fix this, edit your .vnc/xstartup file to contain:

```
#!/bin/sh

[ -r /etc/sysconfig/i18n ] && . /etc/sysconfig/i18n
export LANG
export SYSFONT
vncconfig -iconic &
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
OS=`uname -s`
if [ $OS = 'Linux' ]; then
  case "$WINDOWMANAGER" in
    *gnome*)
      if [ -e /etc/SuSE-release ]; then
        PATH=$PATH:/opt/gnome/bin
        export PATH
      fi
      ;;
  esac
fi
if [ -x /etc/X11/xinit/xinitrc ]; then
  exec /etc/X11/xinit/xinitrc
fi
if [ -f /etc/X11/xinit/xinitrc ]; then
  exec sh /etc/X11/xinit/xinitrc
fi
[ -r $HOME/.Xresources ] && xrdb $HOME/.Xresources
xsetroot -solid grey
xterm -geometry 80x24+10+10 -ls -title "$VNCDESKTOP Desktop" &
twm &
```
