#!/bin/sh
set -eu
cd "$(dirname "$0")"
npx --no-install esbuild src/entry.js --bundle --minify --platform=browser --outfile=bundle.min.js
