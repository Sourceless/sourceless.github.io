#!/bin/bash

rm -rf dist
mkdir -p dist
mkdir -p dist/posts
lein run
cp -r assets dist/assets
