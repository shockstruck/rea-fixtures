#!/bin/sh
set -eu
cd "$(dirname "$0")"
DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 dotnet build Fixture.csproj --configuration Release --output out
cp out/Fixture.dll Fixture.dll
