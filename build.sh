#!/bin/bash

if [[ -z $1 ]]; then
    echo setting default url
    URL="file://$(pwd)/dist"
else
    URL=$1
fi

rm -rf dist
mkdir -p dist
mkdir -p dist/posts
lein run $URL
cp -r assets dist/assets
