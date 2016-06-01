#!/bin/bash
##############################################################################
#
# Copyright 2016 KPMG Advisory N.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
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
# Simple script to set up the KAVE environment
# called automatically from /etc/profile.d if the installer has
# been run.

# touch ~/.nokaveEnv to disable the automatic calling of the script

# touch .kaveEnv to force automatic calling of the script unless .nokaveEnv is present

# touch ~/.nokaveBanner to disable printing the banner


## Begin KaveToolbox
# ^ don't remove this line from this script!
# this is the "local install" script, with default parameters it will be overwritten if installed for all users at the top level ...
# work out where this script is running from, will setup environment
# based on this directory

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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
		if [ -e $DIR/../Welcome.banner ]; then
			cat $DIR/../Welcome.banner
		fi
	fi
fi

export KAVETOOLBOX=${DIR}'/../'

#only add directories to path if they are not already there!
if [[ ":$PATH:" == *":$DIR/../bin:$DIR/../scripts:"* ]]; then
	true
else
	export PATH=${DIR}"/../bin:"${DIR}"/../scripts:"${PATH}
fi

if [[ ":$PYTHONPATH:" == *":$DIR/../python:"* ]]; then
	true
else
	export PYTHONPATH=${DIR}"/../python:"${PYTHONPATH}
fi

#Add spark if spark is installed
if type pyspark >/dev/null 2>/dev/null ; then
  export SPARK_HOME=`readlink -f \`which pyspark\``
  export SPARK_HOME=`dirname \`dirname $SPARK_HOME\``

  if [[ ":$PYTHONPATH:" == *":$SPARK_HOME/python:"* ]]; then
    true
  else
    export PYTHONPATH=${SPARK_HOME}"/python:"${PYTHONPATH}
  fi
fi

#
# \/ don't remove this line from this script!
## End KaveToolbox