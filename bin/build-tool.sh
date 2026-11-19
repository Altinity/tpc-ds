#!/bin/bash

cd ../tpc-ds-tool/v2.11.0rc2/tools

# The TPC-DS tools are old C code (implicit int, K&R declarations). Recent gcc rejects them
# (gcc 14 made implicit int an error; gcc 15 defaults to C23; tested with gcc 15.2), so build as gnu89.
make -f Makefile.suite OS=LINUX CC="gcc -std=gnu89 -fcommon -w" > make.out 2>&1 || exit -1
rm make.out
