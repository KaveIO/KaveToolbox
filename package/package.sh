#!/bin/bash
##############################################################################
#
# Copyright 2016 KPMG N.V. (unless otherwise stated)
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
#
# This is the release package builder. It will create things in the build directory for you.
# If you are not a dev, then just don't do this! Once it's done, making a release means
#     1. Checking all the tags in the welcome banner and the release notes
#     2. Testing the installer, tagging the project
#     3. re-running on the tagged directory
#     4. Upload the install script to the correct noarch directory
#     5. download the source tarball from git and upload to the correct noarch directory, with the correct name
#
#

#abort at first failure
set -e
#set -o pipefail #not a good idea, causes failures even in actual successful situations

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"
BUILD_DIR=$PROJECT_DIR/build
TMP_DIR=/tmp/tempbuild

cd $PROJECT_DIR
TAG=`git name-rev --tags --name-only $(git rev-parse HEAD)`
TAG=`echo ${TAG} | sed s'/\^0//' | sed s'/\^//'`
echo $TAG


# Make the build directory
mkdir -p $BUILD_DIR
rm -rf $BUILD_DIR/*
################################################################
# Build the package tarball
################################################################
RELEASE_PACKAGE="kavetoolbox-$TAG.tar.gz"
echo "Building $RELEASE_PACKAGE"
#mkdir -p $BUILD_DIR/package/kavetoolbox/
#cp -r $SRC_DIR/HDP $BUILD_DIR/package/ambari-server/resources/stacks/
if [ -d $TMP_DIR ]; then
	rm -rf $TMP_DIR/*
fi
mkdir -p $TMP_DIR

# Tar autocollapses. If I'm not in the same path as I'm taring than my tarball
# contains the full path.
cd $PROJECT_DIR/..
cp -r `basename $PROJECT_DIR` $TMP_DIR/KaveToolbox
cd /tmp/tempbuild/
#remove pyc files!
find . -name "*.pyc" -exec rm '{}' ';'
tar -czf $RELEASE_PACKAGE KaveToolbox
mv $RELEASE_PACKAGE $BUILD_DIR
cd $PROJECT_DIR

################################################################
# Write the actual installation script to the file
################################################################
RELEASE_INSTALLER="kavetoolbox-installer-$TAG.sh"
echo "Writing the noarch installer: $RELEASE_INSTALLER"

echo '#!/bin/bash' > $BUILD_DIR/$RELEASE_INSTALLER
cat $PROJECT_DIR/LICENSE >> $BUILD_DIR/$RELEASE_INSTALLER
echo '' >> $BUILD_DIR/$RELEASE_INSTALLER

cat << EOF >> $BUILD_DIR/$RELEASE_INSTALLER
#
# The auto install script, passes all arguements to the KaveInstall script. For more details on the arguments, try --help
#
#
# NB: the repository server uses a semi-private password only as a means of avoiding robots and reducing DOS attacks
#  this password is intended to be widely known and is used here as an extension of the URL
#
repos_server="http://repos:kaverepos@repos.kave.io/"
checkout="wget"
if [ -f /etc/kave/mirror ]; then
	while read line
	do
		#echo \$line
		if [ -z "\$line" ]; then
			continue
		fi
		#always add a trailing /
		if [ "\${line: -1}" != '/' ]; then
			line=\${line}/
		fi
		if [[ ! "\$line" =~ "http" ]]; then
			if [ -d "\$line" ]; then
				checkout="cp"
				repos_server=\${line}
				break
			fi
			continue
		fi
		res=\`curl -i -X HEAD "\$line" 2>&1\`
		#echo \$res
		if [[ "\$res" =~ "200 OK" ]]; then
			repos_server=\${line}
			break
		elif  [[ "\$res" =~ "302 Found" ]]; then
			repos_server=\${line}
			break
		fi
	done < /etc/kave/mirror
fi

# abort at first failure below this line!
set -e

if [ ! -f $RELEASE_PACKAGE ]; then
	#echo \${checkout} \${repos_server}
	\${checkout} \${repos_server}noarch/KaveToolbox/$TAG/$RELEASE_PACKAGE
fi
tar -xzf $RELEASE_PACKAGE
#try to cope with the annoying way the git-generated tarball contains something with .git at the end!
if [ -d kavetoolbox.git ]; then
	mv kavetoolbox.git kavetoolbox
fi
EOF

echo './[k,K]ave[t,T]oolbox*/scripts/KaveInstall $@' >> $BUILD_DIR/$RELEASE_INSTALLER
