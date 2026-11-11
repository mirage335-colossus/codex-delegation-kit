#!/bin/sh
set -eu
test "$#" -eq 1
g++ -O3 -std=c++17 -Wall -Wextra -pedantic "$(dirname "$0")/core.cpp" -o "$1"
