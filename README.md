## altinity-tpc-ds
ClickHouse TPC-DS (Decision Support Benchmark).

## Benchmark environment
* Data scale = 100 (100GB of data)
* Node size 16 CPU, 64GB RAM
* ClickHouse server version 23.2

## Report

72 queries passing (72.73%)

### 1. Performance issues

#### 1.1 '600s timeout'


| **Affected queries** ||
| --- | --- |
| [query_72.sql](/queries/query_72.sql) | 

### 2. Fixable failed queries

Fixes described below will require modification of related template-files or generated queries.

#### 2.1.1 'There is no supertype for types Float32, Decimal(7, 2) because some of them have no lossless conversion to Decimal., not supported'

[github issue 9881](https://github.com/ClickHouse/ClickHouse/issues/9881)

To fix: need to explicitly cast *Float64* to *Decimal(7, 2)*.


| **Affected queries** ||
| --- | --- |
| [query_5.sql](/queries/query_5.sql) | 

#### 2.4 Intervals like this '+ 30 days' not supported

[github issue 9887](https://github.com/ClickHouse/ClickHouse/issues/9887#issuecomment-763397937)

To fix: need to use *INTERVAL* data type.

```sql
# fail
SELECT (now() + 30 days);

# success
SELECT (now() + INTERVAL 30 day);
```

| **Affected queries** ||
| --- | --- |
| [query_12.sql](/queries/query_12.sql) | [query_40.sql](/queries/query_40.sql) |
| [query_16.sql](/queries/query_16.sql) | [query_82.sql](/queries/query_82.sql) |
| [query_21.sql](/queries/query_21.sql) | [query_92.sql](/queries/query_92.sql) |
| [query_32.sql](/queries/query_32.sql) | [query_94.sql](/queries/query_94.sql) |
| [query_37.sql](/queries/query_37.sql) | |


### 3. FAILED queries

#### 3.1 Memory limit exceeded (Could be a part of Performance optimization)

```bash
Code: 241. DB::Exception: Received from localhost:9000. DB::Exception: Memory limit (for query) exceeded: would use 32.34 GiB (attempt to allocate chunk of 67108864 bytes), maximum: 32 GiB.
```
 
| **Affected queries** | | |
| --- | --- | --- |
| [query_4.sql](/queries/query_4.sql) | [query_13.sql](/queries/query_13.sql) | [query_14.sql](/queries/query_14.sql) |
| [query_18.sql](/queries/query_18.sql) | [query_48.sql](/queries/query_48.sql) ||
| [query_65.sql](/queries/query_65.sql) | [query_78.sql](/queries/query_78.sql) ||

*Remark:* when run test under Docker, make sure that the memory limit much more [max_memory_usage](https://clickhouse.tech/docs/en/operations/settings/query_complexity/#settings_max_memory_usage) (see Docker -> Settings -> Advance).

#### 3.5 CASE operator in ORDER BY

[github issue 46335](https://github.com/ClickHouse/ClickHouse/issues/46335)

```sql
SELECT key_a + key_b as d, rank() OVER () as f FROM (SELECT rand() % 10 as key_a, rand(1) % 5 as key_b, number  FROM numbers(100)) GROUP BY rollup(key_a,key_b) ORDER BY  case when d = 0 then key_a end;

Code: 47. DB::Exception: Unknown column: if(equals(plus(key_a, key_b), 0), key_a, NULL), there are only columns __grouping_set, key_a, key_b, plus(key_a, key_b). (UNKNOWN_IDENTIFIER)
```


| **Affected queries** |||
| --- | --- | --- |
| [query_36.sql](/queries/query_36.sql) | [query_70.sql](/queries/query_70.sql) | [query_86.sql](/queries/query_86.sql) |


#### 3.7.3 'Correlated subqueries (missing columns: "x" while processing query)'

[github issue 6697](https://github.com/ClickHouse/ClickHouse/issues/6697)

```sql
# success
SELECT dummy, name
FROM system.one, system.columns
WHERE (SELECT count() FROM system.columns WHERE name != '') > 0 AND dummy = 0
LIMIT 1;

# fail
SELECT dummy, name
FROM system.one, system.columns
WHERE (SELECT count() FROM system.columns WHERE name != '' AND dummy = 0) > 0
LIMIT 1;

# fail
SELECT o.dummy, name
FROM system.one o, system.columns
WHERE (SELECT count() FROM system.columns WHERE name != '' AND o.dummy = 0) > 0
LIMIT 1;
```

| **Affected queries** |||
| --- | --- | --- |
| [query_6.sql](/queries/query_6.sql) | [query_10.sql](/queries/query_10.sql) | [query_16.sql](/queries/query_16.sql) |
| [query_30.sql](/queries/query_30.sql) | [query_32.sql](/queries/query_32.sql) | [query_35.sql](/queries/query_35.sql) |
| [query_41.sql](/queries/query_41.sql) | [query_69.sql](/queries/query_69.sql) | [query_81.sql](/queries/query_81.sql) |
| [query_92.sql](/queries/query_92.sql) | [query_94.sql](/queries/query_94.sql) | [query_1.sql](/queries/query_1.sql) |


#### 3.7.8 'CROSS JOIN to INNER JOIN rewrite depends on tables order in query.'

[github issue 9194](https://github.com/ClickHouse/ClickHouse/issues/9194)

| **Affected queries** |
| --- |
| [query_18.sql](/queries/query_18.sql) |
| [query_65.sql](/queries/query_65.sql) |


#### 3.7.9 'There is no supertype when CROSS to INNER JOIN rewrite WHERE a.key=b.key-1'

[github issue 21794](https://github.com/ClickHouse/ClickHouse/issues/21794)

| **Affected queries** |
| --- |
| [query_47.sql](/queries/query_47.sql) |
| [query_57.sql](/queries/query_57.sql) |


## References

### TPC-DS documents

[TPC-DS Tools](http://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp) or take [already downloaded](/assets/9b0e0c62-e2be-4183-9a51-de7de896b71d-tpc-ds-tool.zip)

### Others DB benchmarks

[Vertica White paper - Benchmarks Prove the Value of an Analytical Database for Big Data](https://www.vertica.com/wp-content/uploads/2017/01/Benchmarks-Prove-the-Value-of-an-Analytical-Database-for-Big-Data.pdf)

[Vertica TPC-DS benchmark performance analysis](http://bicortex.com/vertica-mpp-database-overview-and-tpc-ds-benchmark-performance-analysis-part-3/)

[tidb-bench](https://github.com/pingcap/tidb-bench)
