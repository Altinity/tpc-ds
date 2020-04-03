#!/bin/bash

mkdir -p ~/clickhouse_volumes/tpc-ds
docker run -d --name clickhouse-server --ulimit nofile=262144:262144 --volume=$HOME/clickhouse_volumes/tpc-ds:/var/lib/clickhouse yandex/clickhouse-server