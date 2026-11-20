#!/bin/bash

CLICKHOUSE_VERSION="${CLICKHOUSE_VERSION:-26.10.7.24}"

mkdir -p ~/clickhouse_volumes/tpc-ds
docker run -d --name clickhouse-server --ulimit nofile=262144:262144 --cap-add=SYS_NICE --cap-add=IPC_LOCK \
    --volume=$HOME/clickhouse_volumes/tpc-ds:/var/lib/clickhouse clickhouse/clickhouse-server:$CLICKHOUSE_VERSION
