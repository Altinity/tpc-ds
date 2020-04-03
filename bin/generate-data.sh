#!/bin/bash

if [ "$#" != 1 ]; then
    echo "Missing SCALE factor param (GB)."
    exit 1
fi

cd ../tpc-ds-tool/v2.11.0rc2/tools
OUTPUT_DIR="../../../data"

if [ -d $OUTPUT_DIR ]; then
    echo "It looks like data already generated. Remove/rename the 'data'-directory to generate it again."
    exit 1
fi

SCALE=$1
SUFFIX="_$(printf "%04d" $SCALE).dat"

mkdir $OUTPUT_DIR
./dsdgen -scale $SCALE -dir $OUTPUT_DIR -suffix $SUFFIX

cd -