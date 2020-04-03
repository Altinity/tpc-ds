#!/bin/bash

cd ../tpc-ds-tool/v2.11.0rc2/tools

make -f Makefile.suite OS=LINUX > make.out 2>&1 || exit -1
rm make.out