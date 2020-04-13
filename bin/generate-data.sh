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
PARALLEL_STREAMS_COUNT=64

mkdir $OUTPUT_DIR

for ((i = 1; i <= $PARALLEL_STREAMS_COUNT; i++)); do
	./dsdgen -scale $SCALE -dir $OUTPUT_DIR -suffix $SUFFIX -parallel $PARALLEL_STREAMS_COUNT -child $i &
    pids[${i}]=$!
done

# wait for generating be completed
for pid in ${pids[*]}; do
    wait $pid
done

cd -