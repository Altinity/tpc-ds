#!/bin/bash
# Load the dsdgen output into ClickHouse.
#   ./upload-data.sh [data_dir]            (default: ../data)
# Env: CLICKHOUSE_CLIENT  client command (default: clickhouse-client)
#      PARALLEL           files loaded concurrently (default: 8)
# dsdgen -parallel N names files <table>_<child>_<N>_<scale>.dat; the table
# name is everything before those three numeric suffixes.

DATA_DIR="${1:-../data}"
CLIENT="${CLICKHOUSE_CLIENT:-clickhouse-client}"
PARALLEL="${PARALLEL:-8}"

load_file() {
    file_name="$1"
    table_name=$(basename "$file_name" | sed -E "s/(_[0-9]+){3}\.dat$//" | tr "[:upper:]" "[:lower:]")
    echo "INSERT INTO $table_name <-- $(du -h "$file_name" | cut -f1) $(basename "$file_name")"
    $CLIENT --format_csv_delimiter="|" --max_partitions_per_insert_block=100 \
        --database="tpcds" --query="INSERT INTO $table_name FORMAT CSV" < "$file_name" \
        || echo "FAILED: $file_name" >&2
}
export -f load_file
export CLIENT

ls "$DATA_DIR"/*.dat | xargs -P "$PARALLEL" -I{} bash -c "load_file {}"
