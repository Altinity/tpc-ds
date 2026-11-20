## Infrastructure preparation

### Create DB

1. prepare CH database with required scale

All scripts are run from the `bin` directory.

```bash
git clone https://github.com/Altinity/tpc-ds.git
cd tpc-ds/bin

./build-tool.sh
./generate-data.sh 100 # 100 is scale; fails if ../data already exists, move it away first

# the client: a local clickhouse-client, or for a server started by start-clickhouse-server.sh (no published port):
#   export CLICKHOUSE_CLIENT="docker exec -i clickhouse-server clickhouse-client"
${CLICKHOUSE_CLIENT:-clickhouse-client} -mn < ../schema/tpcds.sql

./upload-data.sh # optional arg: data dir (default ../data); env PARALLEL (default 8), CLICKHOUSE_CLIENT

# script to monitoring DB size
# while :; do sudo du -hs /var/lib/clickhouse/data/tpcds; sleep 90; done
```

The uploader keeps the .dat files; delete them yourself when done.

2. check the correctness of CH database

Compare the count of rows with [TPC DS Specification (see '3.2 TEST DATABASE SCALING')](https://github.com/Altinity/tpc-ds/blob/master/tpc-ds-tool/v2.11.0rc2/specification/specification.pdf) per table.

### Run the queries

```bash
./run_queries.py --runs 2 --timeout 600 --out results/results.csv # uses CLICKHOUSE_CLIENT like upload-data.sh

# chart of two result files (edit the two CSV names at the top of the script)
python3 make_chart.py
```
