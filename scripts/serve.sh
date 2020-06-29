#!/usr/bin/env sh

cd .site
rm -rf source/i source/_posts
cp -r ../i ../_posts source/
npm run serve
