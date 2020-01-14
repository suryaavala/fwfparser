#!/bin/bash

if [ "$1" == "local" ]; then
# build image locally and run
IMAGE=fwfparser:test
docker build --target test --file Dockerfile -t fwfparser:test .
shift
else
# pull image from docker hub and run
IMAGE=suryaavala/fwfparser:test
docker pull $IMAGE 
fi

docker run $IMAGE