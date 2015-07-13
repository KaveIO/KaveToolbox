# The ReleaseNotes file

Contains a list of the released versions with a summary of the main changes in each version.


# Beta Releases

## v1.2-Beta

* Major fixes for Ubuntu and Centos7


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
