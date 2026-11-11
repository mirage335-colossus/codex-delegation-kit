#!/bin/sh
set -eu
g++ --version | head -1
td=$(mktemp -d ./.probe.XXXXXX)
trap 'rm -rf "$td"' EXIT
g++ -std=c++17 -O3 -x c++ -o "$td/probe" - <<'CPP'
#include <iostream>
int main(){std::cout << "cxx17-ready\n";}
CPP
"$td/probe"
