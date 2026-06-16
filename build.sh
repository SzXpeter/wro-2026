#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/tmp/lego_build"
OUTPUT_DIR="$SCRIPT_DIR/build"


rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
mkdir -p "$OUTPUT_DIR"
cd "$BUILD_DIR"

cmake "$SCRIPT_DIR/cpp" \
    -DCMAKE_TOOLCHAIN_FILE="$SCRIPT_DIR/toolchain-pi3.cmake" \
    -DCMAKE_BUILD_TYPE=Release

make -j$(nproc)

# cp "$BUILD_DIR/libcalculator.so" "$OUTPUT_DIR/libcalculator.so"
cp "$BUILD_DIR/librobot.so"     "$OUTPUT_DIR/librobot.so"

echo ""
echo "Build sikeres:"
# file "$OUTPUT_DIR/libcalculator.so"
file "$OUTPUT_DIR/librobot.so"
