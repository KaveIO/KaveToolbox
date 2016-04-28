# The ReleaseNotes file

Contains a list of the released versions with a summary of the main changes in each version.

# Beta Releases

## v2.0-Beta

Major version change, mirroring the version increase of AmbariKave

Major changes:
* Version numbering: for all the packages we install to the topdir (/opt by default), we now add version subdirectories
  Each directory also has a pro softlink, which is created during install. Advanced users may wish to modify this softlink
  This versioning scheme has several benefits:
  a) Ability to have multiple KTB versions operating side-by-side
     (to start a different KTB run the KaveEnv script with the version as a parameter, i.e. KaveEnv.sh 2.0-Beta)
  b) Simpler upgrading
     (no need to delete /opt content yourself before the upgrade, if needed the script can do that for you
     with --clean-after, or --clean-if-disk-full, see the installation help for more new flags)
* Affect of version numbering on script locations: the KaveToolbox distribution used to be placed under
  /topdir/KaveToolbox directly (e.g. /opt/KaveToolbox/scripts/KaveEnv.sh). Now it is moved to a versioned directory
  (e.g. /opt/KaveToolbox/2.0-Beta/scripts/KaveEnv.sh). Scripts which explicitly source the env file or bind against
  explicit directories will need to be updated accordingly, either to point to the new static location, or to point
  to the new dynamic location (e.g.: /opt/KaveToolbox/2.0-Beta/pro/KaveEnv.sh)
* We have created an update script can poll for latest versions from the repository.
  The new KaveUpdate script will poll the repo server for latest versions and install what you request
* KaveEnv script will now take a version arguement to enable a specific version (pro by default)

Minor changes:
* Default ROOT version update to 5.34.36
* New pip packages for kave integration: pymongo and pykerberos
* Additional flags to the installation script, see the installation help
* pygsl protected against continuous re-install if it already exists
* Consolodation of java versions, openjdk-1.8 is preferred
* xpdf added to default workstation install
* Installer is now aware of how much disk space is required and will warn you or fail
  if insufficient disk space is available. You can choose from a broad list of options
  on what to do in this case, e.g.: --clean-if-disk-full, or --clean-after, or
  --skip-if-disk-full, or --clean-before
* refactoring of code to adhere to pep8 standard for function names where possible
* addition of unit test framework copied from similar AmbariKave project

Bugfixes:
* pygsl protected against continuous re-install if it already exists
* rootpy install issues (unreliable failures) fixed
* Vnc install on Centos7 updated
* eliminate unrealiable dumbo library from standard installation

* Note about Robomongo:
 - We have added the installation instructions for robomongo, but we do not install it by default
 - This is because Robomongo does not support Mongo 3.0, to which we are migrating
 - Users can manually install robomongo 0.8.4 by setting the correct configuration flag in CustomInstall.py
 - cnf.robo.doInstall=True,  cnf.robo.workstation=True

* Note about pentaho kettle
 - We have updated the installed version of Pentaho (Kettle) to 5.4
   Pentaho DI 5.4 does not currently have native support for HDP 2.4 at the time of this release
   Version 6 has been released but is not included in KaveToolbox yet, since there are several major
   bugs preventing use, and the size of the kettle download has grown very very large in 6.0

* Note about Gnome and Centos:
 - We install gnome in workstation mode Centos6/7 to get a good enough vnc session for most users
 - There are two gnome packages/plugins that I do not want to install/run: NetworkManager and PulseAudio
 - NetworkManager: problems seen within a VM trying to control the network config. It's not necessary within a VM.
 - PulseAudio: spams logfiles of VMs where there is no virtual soundcard installed. It's not necessary within a VM.
 - However, these two now are static forced dependencies within the gnome installation, so they are not skippable
 - I can skip NetworkManager on Centos6, but no further skipping options work right now.
 - Currently then I don't know how to install a sufficiently good desktop tool without these plugins

## v1.4-Beta

* Minor release with incremental fixes and small version updates

* Update to Anaconda 2.4
* Update to ROOT 5.34.34
* add pygsl and py4j
* add spark python to python path if spark is available
* Fix some issues with x-installation on ubuntu (would always re-install X)
* Rename a lot of examples
* Code review of modules in our python directory
* Adjust ProtectNotebooks.py to work with Jupyter as well as old ipython
* Fix packaging/installation script so that it copes with missing repositories in the mirrors file

## v1.3-Beta

* Bugfix release with high-impact fixes for Ubuntu and Centos7

New features:

* 10 KAVE wallpapers in KaveToolbox/figs (applied automatically for Centos6 workstation installs)
* ProtectNotebooks.sh script: if run as root, will add a system-wide ipython\_notebook\_config.py file
                              if run as a user will add a user-level ipython\_notebook\_config.py file
                              this file chooses a default port based on username and protects notebooks with the user's login password
* improved the customizability of the DefaultInstall parameters to enable simpler future hotfixes
* additional python visualization libraries installed by default (pygal, mpd3, seaborn, cairosvg, vincent) new example notebooks
* additional python geometry/geography libraries installed by default (shapely, pyproj, descartes, folium) new example notebooks
* install pyhs2 by default (python hive client)
* add mathmore and gsl for ROOT
* add rootpy library in case ROOT is installed (allows pickling python objects and storing in root files)
* JSON highlighting in eclipse
* Additional features to rootnotes including IPython magic functions


Bugfixes:

* libpng15 installation added for centos7 and ubuntu platforms
* ROOT rebuilt on latest centos 7 and ubuntu 14 platforms
* missing yum groups no longer causes spurious failures or false positives on ubuntu and centos7
* automatic testing on centos6 and ubuntu 14 performed
* Accidental inclusion of specific developer environment in eclipse distribution removed
* fix mistake in KaveEnv source statement for ROOT causing failures on ubuntu and centos7
* fix mistake in default download directory from the repo
* fix rpy installation on Ubuntu
* add installation of vncserver to ubuntu if not already installed to avoid gnome/kde issues
* clean tmpdir at the end of each step to save space during install (saves up to 3 GB)


## v1.2-Beta

* Minor bugfixes in packaging and installer script

* Installer now checks that yum groups exist since it was noticed groups are fragile on many centos6 systems
* Packaged installer now fails on the first encountered error rather than proceeding blindly
* Installer now less sensitive to trailing '/' in /etc/kave/mirror which previously could cause failures in some wget calls

## v1.1-Beta

* Reworking of the postalmap package to be more generic
* Minor updates in the installer to install curl and wget
* Move to anaconda 2.2.0 from 2.1.0

## v1.0-Beta

* First version of KaveToolbox ready for wider distribution
* Added R, integrated with python and ipython notebooks
* Added Kettle, the open source pentaho equivalent
* Migrated packages to our repo server and implemented functions to obtain those packages
* Major refactoring of the installer to add a common configuration location of /etc/kave/CustomInstall.py
* Read contents of /etc/kave/mirror to see if there is a local checkout of the repository or a near-side cache

# Alpha Releases

## v0.1

* First stable KaveToolbox
* Root Anaconda(SciPy) Eclipse and some small libraries
* Node or Workstation mode
* Clear configuration file
* No upgrade mechanism
