#! /bin/bash
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
###############################################################################
# Test runner script, unit tests are runnable without specific local installation
# further tests require aws availability, aws configuration, and AWSSECCONF variable defined
#

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$CURRENT_DIR/../python:$CURRENT_DIR/../tests/base:$CURRENT_DIR/../config:$PYTHONPATH
export BAHDIR=$CURRENT_DIR

if [ ! -z "$1" ]; then
	python $@
	exit $?
fi


########## TDD stats
echo "============================= TDD STATS =============================="
date --utc
mbc=`find ${BAHDIR}/.. -type f -name '*.*' | grep -v .git | grep -v .geojson | grep -v .ipynb | grep -v .csv | grep -v .pyc | grep -v .png | grep -v .md | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l`
mtc=`find ${BAHDIR} -type f -name '*.*' | grep -v .pyc | grep -v .md | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l`
mlc=$(($mbc-$mtc))
tdd=`python -c "print float($mtc) / $mlc"`
echo "TDD Stats, Code:Test " $mlc:$mtc "ratio:" $tdd
########## Unit tests
echo "============================= UNIT TESTS ============================="
date --utc
python $CURRENT_DIR/unit/all.py
res=$?
if [[ $res -ne 0 ]] ; then
	exit 1
fi

######### Succeeded
date --utc
echo "OK"
