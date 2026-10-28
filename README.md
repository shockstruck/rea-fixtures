# REA synthetic fixtures

Small synthetic artifacts for testing file and binary analysis. Each directory
contains the source and script used to rebuild its fixture.

## Fixtures

- `js/bundle.min.js`: a bundled and minified pair of tiny JavaScript modules.
  Rebuild with `cd js && npm ci && ./build.sh`.
- `electron/app.asar`: a small Electron archive with a main process, preload,
  package metadata and one IPC handler. Rebuild with `cd electron && npm ci && ./build.sh`.
- `managed/Fixture.dll`: a minimal .NET class library. Rebuild with
  `cd managed && ./build.sh` after installing the pinned .NET SDK version
  8.0.408 using Microsoft's dotnet-install script.

- `android/minimal.apk`: a minimal APK built from its committed manifest and
  Java activity. Rebuild after installing Temurin JDK 21 and Android SDK
  command-line tools, build-tools 35.0.0 and platform 35, with
  `JAVA_HOME=<jdk-path> ANDROID_SDK_ROOT=<sdk-path> android/build.sh`. The
  script generates a throwaway signing key in a temporary directory and
  deletes it after signing.
