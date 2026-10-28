#!/bin/sh
set -eu
cd "$(dirname "$0")"
ROOT=$(CDPATH= cd -- .. && pwd)
SDK=${ANDROID_SDK_ROOT:-"$ROOT/.toolchains/android-sdk"}
BUILD_TOOLS="$SDK/build-tools/35.0.0"
PLATFORM="$SDK/platforms/android-35"
OUT="$PWD/build"
GEN="$PWD/.generated"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
PATH="${JAVA_HOME:?Set JAVA_HOME to the installed Temurin JDK 21}/bin:$PATH"
export PATH
rm -rf "$OUT" "$GEN"
mkdir -p "$OUT" "$GEN" "$OUT/classes" "$OUT/compiled" "$OUT/dex"

"$BUILD_TOOLS/aapt2" compile --dir res -o "$OUT/compiled"
"$BUILD_TOOLS/aapt2" link -o "$OUT/unsigned.apk" \
  -I "$PLATFORM/android.jar" --manifest AndroidManifest.xml \
  --java "$GEN" --min-sdk-version 23 --target-sdk-version 35 \
  "$OUT/compiled"/*.flat

"$JAVA_HOME/bin/javac" \
  -source 8 -target 8 -bootclasspath "$PLATFORM/android.jar" \
  -d "$OUT/classes" "$GEN"/org/example/syntheticfixture/R.java \
  src/org/example/syntheticfixture/MainActivity.java
"$BUILD_TOOLS/d8" --lib "$PLATFORM/android.jar" \
  --output "$OUT/dex" "$OUT/classes/org/example/syntheticfixture/"*.class
python3 -c "import zipfile; p='$OUT/unsigned.apk'; z=zipfile.ZipFile(p,'a'); z.write('$OUT/dex/classes.dex','classes.dex'); z.close()"

"$JAVA_HOME/bin/keytool" \
  -genkeypair -keystore "$TMP/throwaway.jks" -storepass changeit \
  -keypass changeit -alias fixture -keyalg RSA -keysize 2048 -validity 2 \
  -dname 'CN=Synthetic Fixture'
"$BUILD_TOOLS/zipalign" -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"
"$BUILD_TOOLS/apksigner" sign --ks "$TMP/throwaway.jks" \
  --ks-pass pass:changeit --key-pass pass:changeit --out minimal.apk \
  --v4-signing-enabled false "$OUT/aligned.apk"
"$BUILD_TOOLS/apksigner" verify --verbose minimal.apk
