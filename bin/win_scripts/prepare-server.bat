echo off

echo generate test data to CH storage volume

mkdir %HOME%\DockerVolumes\clickhouse\_tpc-ds-data
cd v2.11.0rc2\tools
dsdgen.exe /scale 1 /dir %HOME%\DockerVolumes\clickhouse\_tpc-ds-data /suffix _001.dat


echo copy DB schema to CH storage volume

mkdir %HOME%\DockerVolumes\clickhouse\_tpc-ds-schema
copy schema\tpcds.sql %HOME%\DockerVolumes\clickhouse\_tpc-ds-schema

