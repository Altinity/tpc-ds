mkdir %HOME%\DockerVolumes\clickhouse
docker run -d --name clickhouse-server --ulimit nofile=262144:262144 --volume=%HOME%\DockerVolumes\clickhouse:/var/lib/clickhouse yandex/clickhouse-server