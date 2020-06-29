#!/usr/bin/env sh

cd .site
cp -r ../i ../_posts source/
npm i
npm run deploy
