#!/bin/bash
set -e
TAG="3.0-Beta"
docker login
for type in c7.node u14.node u16.node c7.workstation u14.workstation u16.workstation; do
	echo $type $TAG "building"
	docker build -t "test/${type}-test" $type
	echo $type $TAG "tagging"
	docker tag "test/${type}-test" "kave/kavetoolbox:${TAG}.${type}"
	echo $type $TAG "pushing"
	docker push "kave/kavetoolbox:${TAG}.${type}"
done
