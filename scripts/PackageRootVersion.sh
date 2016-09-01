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

mhelp='create a tarball of this installed root version. usage PackageRootVersion.sh <directory_to_write_to> [<root_from_here_>=/opt/root/v*]'

# Parse Arguements

for i in "$@" ; do
    if [[ ${i} == "--help" ]] ; then
        echo -e ${mhelp}
        exit 0
    fi
done


if [ -z "$1" ]; then
    echo -e ${help}
    echo "Error: Not enough arguements specified" 1>&2
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

todir=$1
fromdir=/opt/root
rootversion=''

if [ -z "$2" ]; then
    fromdir=`ls -d ${fromdir}/v* | head -n 1 | grep v `
else
	fromdir=$2
fi

set -e
rootversion=`basename $fromdir`
osversion=`${DIR}/DetectOSVersion | tail -n 1 | tr '[:upper:]' '[:lower:]' `
echo $rootversion $osversion $fromdir $todir
cd $todir
cp -r $fromdir root
tar czf root_${rootversion}_${osversion}.tar.gz root
ls root_*
