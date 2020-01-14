#!/bin/bash

if [ "$1" == "local" ]; then
# build image locally and run
IMAGE=fwfparser:latest
docker build --file Dockerfile --target prod --tag $IMAGE .
shift
else
# pull image from docker hub and run
IMAGE=suryaavala/fwfparser:latest
docker pull $IMAGE 
fi

if [ "$#" -eq 0 ]; then
BASEDIR="example"

CURDIR="$BASEDIR/$(date +%Y_%m_%d_%H_%M_%S)" 

mkdir -p "$CURDIR"

echo "Files are generated in $(pwd)/$CURDIR"

cp "$BASEDIR/spec.json" "$CURDIR/spec.json"

docker run --mount type=bind,source="$(pwd)/$CURDIR",target="/app/$CURDIR/" $IMAGE -s "$CURDIR/spec.json" -f "$CURDIR/sample_input.txt" -o "$CURDIR/sample_output.csv"

else
CURDIR=$1
if [ ! -d "$CURDIR" ]; then
echo "Usage: ./generate_parse_files.sh ['local'] DIRECTORY_TO_BIND FWFPARSER_ARGUMENTS 
example: ./generate_parse_files.sh local . -s ./example/spec.json"
exit 1
fi
shift
echo "Files are generated in $(pwd)/$CURDIR"

docker run --mount type=bind,source="$(pwd)/$CURDIR",target="/app/$CURDIR/" $IMAGE $@

fi