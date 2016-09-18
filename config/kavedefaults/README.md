KaveToolbox is separated into modular installable components

Each component inherits from the Component class and contains the
complete instructions for installation on Centos6/7 or Ubuntu14

To overwrite these instructions in the case of local variations we don't recommend you to edit this file.
Instead we suggest to create/add configurations to /etc/kave/CustomInstall.py
For modifying pip packages, you can create/edit the content of /etc/kave/requirements.txt, start from
the contents of requirements.txt in this folder
e.g. adding extra entries like:

```
#-----------------
import kavedefaults as cnf

# overwrite top install directory
cnf.li.InstallTopDir='/wheretostartinstall'

# add an additional step in the pre-install for the toolbox itself
cnf.toolbox.pre['Centos6'].append("yum -y install lynx")

# never install Eclipse
cnf.eclipse.doInstall=False

# install anaconda into a different subdirectory
cnf.conda.installSubDir='whatever_bro'

# change the configuration options of ROOT to add C++11 support if the latest version of gcc is available:
cnf.root.options["conf"]["Centos6"]=cnf.root.options["conf"]["Centos6"] + " --enable-cxx11"
--fail-on-missing""
#-----------------
```