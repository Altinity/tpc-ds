#!/bin/bash

for file_name in `ls ../data/*.dat`; do
    table_file=$(echo "${file_name##*/}")
    table_name=$(echo "${table_file%_*}" | tr '[:upper:]' '[:lower:]')
    upload_data_sql="INSERT INTO $table_name FORMAT CSV"

    echo $file_name
    echo $upload_data_sql

    cat $file_name | clickhouse-client --format_csv_delimiter="|" --max_partitions_per_insert_block=100 --database="tpcds" --query="$upload_data_sql"
done
