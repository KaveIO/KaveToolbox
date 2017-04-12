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
# This file will be copied to profile.d, and will automatically
# add the Kave env at login to a given list of users
# if a user has .kaveEnv in their home directory it will always be called
# if they have .nokaveEnv it will not be called

autoFire='yes'

case `whoami` in
	root)
	 autoFire='no'
	;;
	ams)
     autoFire='no'
    ;;
	postgres)
	 autoFire='no'
	;;
	zookeeper)
	 autoFire='no'
	;;
	ambari-qa)
	 autoFire='no'
	;;
	hdfs)
	 autoFire='no'
	;;
	yarn)
	 autoFire='no'
	;;
	hive)
	 autoFire='yes'
	;;
esac

if [ ! -z "$HOME" ]; then
	if [ -d "$HOME" ]; then
		if [ -e  "$HOME"/.kaveEnv ]; then
			autoFire='yes'
		fi
		if [ -e  "$HOME"/.nokaveEnv ]; then
			autoFire='no'
		fi
	fi
fi

# %ENVSCRIPT% will be replaced when this file is copied to /etc/profile.d/

if [ -e %ENVSCRIPT% ]; then
	if [ ${autoFire} == 'yes' ]; then
	 	 source %ENVSCRIPT%
	fi
fi
