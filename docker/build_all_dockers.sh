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
set -e
TAG="3.6-Beta"
docker login
for type in c7.node u14.node u16.node c7.workstation u14.workstation u16.workstation; do
	echo $type $TAG "building"
	docker build -t "test/${type}-test" $type
	echo $type $TAG "tagging"
	docker tag "test/${type}-test" "kave/kavetoolbox:${TAG}.${type}"
	echo $type $TAG "pushing"
	docker push "kave/kavetoolbox:${TAG}.${type}"
done
