#!/bin/sh
set -eu
cd "$(dirname "$0")"
npx --no-install asar pack fixture app.asar
