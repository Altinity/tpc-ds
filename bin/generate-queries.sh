#!/bin/bash

if [ "$#" != 1 ]; then
    echo "Missing SCALE factor param (GB)."
    exit 1
fi

SCALE=$1

cd ../tpc-ds-tool/v2.11.0rc2/tools

TEMPLATE_DIR="../query_templates"
OUTPUT_DIR="../queries"
DIALECT_FILE="../../../clickhouse-dialect"
QUERY_ID=""

function generate_query()
{
    ./dsqgen \
	    -DIRECTORY "$TEMPLATE_DIR" \
	    -INPUT "$TEMPLATE_DIR/templates.lst" \
	    -SCALE $SCALE \
	    -OUTPUT_DIR $OUTPUT_DIR \
	    -DIALECT $DIALECT_FILE \
	    -TEMPLATE "query$QUERY_ID.tpl" \
	    -VERBOSE Y

    mv "$OUTPUT_DIR/query_0.sql" "$OUTPUT_DIR/query_$QUERY_ID.sql"
}

rm -rf $OUTPUT_DIR
mkdir $OUTPUT_DIR

for i in {1..99}; do
    QUERY_ID="$i"
    generate_query
done

rm -rf ../../$OUTPUT_DIR
mv -f $OUTPUT_DIR ../../..
cd -