#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -x .dotnet/dotnet ]; then
  dotnet_cmd=.dotnet/dotnet
else
  dotnet_cmd=dotnet
fi
sdk_version=$(DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 "$dotnet_cmd" --version)
if [ "$sdk_version" != "8.0.408" ]; then
  printf 'Expected .NET SDK 8.0.408, got %s\n' "$sdk_version" >&2
  exit 1
fi
rm -rf out obj
mkdir -p out
DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 "$dotnet_cmd" build Fixture.csproj --configuration Release --output out
cp out/Fixture.dll Fixture.dll
DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 "$dotnet_cmd" pack Fixture.csproj --configuration Release --no-build --no-restore --output out/raw-packages -p:OutputPath=out/ -p:ContinuousIntegrationBuild=true -p:Deterministic=true -p:EnableSourceControlManagerQueries=false -p:DebugType=None -p:DebugSymbols=false
python3 build-nupkg.py out/raw-packages/Fixture.1.0.0.nupkg Fixture.nupkg
python3 build-zip.py
