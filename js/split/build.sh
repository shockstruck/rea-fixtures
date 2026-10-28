#!/bin/sh
set -eu
cd "$(dirname "$0")"
rm -rf dist
../node_modules/.bin/esbuild src/main.js src/secondary.js \
  --bundle --splitting --format=esm --outdir=dist \
  --entry-names='[name]' --chunk-names='chunks/[name]-[hash]'
