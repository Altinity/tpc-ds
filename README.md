## altinity-tpc-ds
ClickHouse TPC-DS (Decision Support Benchmark).

## Benchmark environment
* data scale = 1 (1GB of data)
* ClickHouse server version 20.3.2.1 revision 54433

## Report

### 1. Working queries out of box or with minor fixes

| queries |||||
| --- | --- | --- | --- | --- |
| [query_3.sql](/queries/query_3.sql) | [query_21.sql](/queries/query_21.sql) [*] | [query_37.sql](/queries/query_37.sql) [*] | [query_55.sql](/queries/query_55.sql) | [query_96.sql](/queries/query_96.sql) [*] |
| [query_9.sql](/queries/query_9.sql) | [query_22.sql](/queries/query_22.sql) | [query_42.sql](/queries/query_42.sql) | [query_62.sql](/queries/query_62.sql) | [query_99.sql](/queries/query_99.sql) |
| [query_17.sql](/queries/query_17.sql) | [query_25.sql](/queries/query_25.sql) | [query_43.sql](/queries/query_43.sql) | [query_65.sql](/queries/query_65.sql) [*] | |
| | [query_28.sql](/queries/query_28.sql) [*] | [query_50.sql](/queries/query_50.sql) | [query_82.sql](/queries/query_82.sql) [*] | |
| [query_19.sql](/queries/query_19.sql) | [query_29.sql](/queries/query_29.sql) | [query_52.sql](/queries/query_52.sql) | [query_84.sql](/queries/query_84.sql) | |

[*] query required some minor fixes (see related remarks below)

### 2. Fixable failed queries

Fixes described below will require modification of related template-files or generated queries.

#### 2.1 'Illegal types Float64 and Decimal(9, 2) of arguments of function multiply'

[github issue 9881](https://github.com/ClickHouse/ClickHouse/issues/9881)

To fix: need to explicitly cast *Float64* to *Decimal(7, 2)*.

```sql
# fail
SELECT toDecimal32(10, 2) > 1.2 * toDecimal32(3, 2);
/* Code: 43. DB::Exception: Received from localhost:9000. DB::Exception: Illegal types Float64 and Decimal(9, 2) of arguments of function multiply. */

# success
SELECT toDecimal32(10, 2) > CAST(1.2, 'Decimal(7, 2)') * toDecimal32(3, 2);
```

| **Affected queries** ||
| --- | --- |
| [query_6.sql](/queries/query_6.sql) | [query_85.sql](/queries/query_85.sql) |
| [query_13.sql](/queries/query_13.sql) | |
| [query_21.sql](/queries/query_21.sql) | |
| [query_48.sql](/queries/query_48.sql) | |
| [query_65.sql](/queries/query_65.sql) | |

#### 2.2 INTERSECT / EXCEPT operators not implemented

To fix: need to use *IN*-operator.

```sql
# fail
SELECT *
FROM (
  SELECT * FROM numbers(2)
  INTERSECT 
  SELECT * FROM numbers(3));

# success
SELECT *
FROM (
  SELECT DISTINCT number FROM numbers(2)
  WHERE number IN (SELECT number FROM numbers(3)));
```

| **Affected queries** |
| --- |
| [query_8.sql](/queries/query_8.sql) |
| [query_38.sql](/queries/query_38.sql) |
| [query_87.sql](/queries/query_87.sql) |

#### 2.3 [NOT] EXISTS-operator not implemented (to test for the existence of rows)

To fix: need to use *count*-aggregate.

```sql
# fail
SELECT 1
WHERE EXISTS (SELECT NULL);

# success
SELECT 1
WHERE (SELECT count() FROM (SELECT NULL)) > 0;

# success
SELECT 1
WHERE (SELECT count() FROM (SELECT 1 WHERE 1 = 0)) > 0;
```

| **Affected queries** |
| --- |
| [query_10.sql](/queries/query_10.sql) |
| [query_16.sql](/queries/query_16.sql) |
| [query_35.sql](/queries/query_35.sql) |
| [query_69.sql](/queries/query_69.sql) |
| [query_94.sql](/queries/query_94.sql) |

#### 2.4 Intervals like this '+ 30 days' not supported

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

#### 3.1 Memory limit exceeded

```bash
Code: 241. DB::Exception: Received from localhost:9000. DB::Exception: Memory limit (for query) exceeded: would use 9.34 GiB (attempt to allocate chunk of 67108864 bytes), maximum: 9.31 GiB.
```
 
| **Affected queries** | | |
| --- | --- | --- |
| [query_7.sql](/queries/query_7.sql) | [query_45.sql](/queries/query_45.sql) | [query_91.sql](/queries/query_91.sql) |
| [query_18.sql](/queries/query_18.sql) | [query_48.sql](/queries/query_48.sql) ||
| [query_13.sql](/queries/query_13.sql) | [query_71.sql](/queries/query_71.sql) ||
| [query_15.sql](/queries/query_15.sql) | [query_76.sql](/queries/query_76.sql) ||
| [query_26.sql](/queries/query_26.sql) | [query_85.sql](/queries/query_85.sql) ||

*Remark:* when run test under Docker, make sure that the memory limit much more [max_memory_usage](https://clickhouse.tech/docs/en/operations/settings/query_complexity/#settings_max_memory_usage) (see Docker -> Settings -> Advance).

#### 3.2 CTE incompatibility

##### Issues
* expression's result contains more than 1 row
* expression's result used in FROM/WHERE clauses
```sql
with customer_total_return as (select .. ) 
select c_customer_id 
from customer_total_return ctr1, /* <-- */
  store, customer 
where ctr1.ctr_total_return > (
    select ..
    from customer_total_return ctr2 /* <-- */
  );
```
* expression name precedes the CTE query definition
```sql
with customer_total_return as (..)
```

| **Affected queries** ||||||
| --- | --- | --- | --- | --- | --- |
| [query_1.sql](/queries/query_1.sql) | [query_14.sql](/queries/query_14.sql) | [query_33.sql](/queries/query_33.sql) | [query_56.sql](/queries/query_56.sql) | [query_64.sql](/queries/query_64.sql) | [query_80.sql](/queries/query_80.sql) |
| [query_2.sql](/queries/query_2.sql) | [query_23.sql](/queries/query_23.sql) | [query_39.sql](/queries/query_39.sql) | [query_57.sql](/queries/query_57.sql) | [query_74.sql](/queries/query_74.sql) | [query_81.sql](/queries/query_81.sql) |
| [query_4.sql](/queries/query_4.sql) | [query_24.sql](/queries/query_24.sql) | [query_47.sql](/queries/query_47.sql) | [query_58.sql](/queries/query_58.sql) | [query_75.sql](/queries/query_75.sql) | [query_83.sql](/queries/query_83.sql) |
| [query_5.sql](/queries/query_5.sql) | [query_30.sql](/queries/query_30.sql) | [query_51.sql](/queries/query_51.sql) | [query_59.sql](/queries/query_59.sql) | [query_77.sql](/queries/query_77.sql) | [query_95.sql](/queries/query_95.sql) |
| [query_11.sql](/queries/query_11.sql) | [query_31.sql](/queries/query_31.sql) | [query_54.sql](/queries/query_54.sql) | [query_60.sql](/queries/query_60.sql) | [query_78.sql](/queries/query_78.sql) | [query_97.sql](/queries/query_97.sql) |

#### 3.3 OVER(PARTITION BY)-clause not implemented

| **Affected queries** ||
| --- | --- |
| [query_12.sql](/queries/query_12.sql) | [query_89.sql](/queries/query_89.sql) |
| [query_20.sql](/queries/query_20.sql) | [query_98.sql](/queries/query_98.sql) |
| [query_53.sql](/queries/query_53.sql) | |
| [query_63.sql](/queries/query_63.sql) | |
| [query_70.sql](/queries/query_70.sql) | |

#### 3.4 RANK OVER(PARTITION BY/ORDER BY)-clause not implemented

| **Affected queries** ||
| --- | --- |
| [query_36.sql](/queries/query_36.sql) | [query_86.sql](/queries/query_86.sql) |
| [query_44.sql](/queries/query_44.sql) | |
| [query_49.sql](/queries/query_49.sql) | |
| [query_67.sql](/queries/query_67.sql) | |
| [query_70.sql](/queries/query_70.sql) | |

#### 3.5 [GROUPING](https://docs.microsoft.com/en-us/sql/t-sql/functions/grouping-transact-sql?view=sql-server-ver15) aggregate function not implemented

| **Affected queries** |
| --- |
| [query_27.sql](/queries/query_27.sql) |
| [query_36.sql](/queries/query_36.sql) |
| [query_70.sql](/queries/query_70.sql) |
| [query_86.sql](/queries/query_86.sql) |

#### 3.6 'Column "x" is not under aggregate function and not in GROUP BY'

| **Affected queries** |
| --- |
| [query_72.sql](/queries/query_72.sql) (need to add alias in *ORDER BY*-clause for column `d_week_seq`) |

#### 3.7 CROSS JOIN errors

##### 3.7.1 'Multiple JOIN do not support asterisks for complex queries yet'

[github issue 9853](https://github.com/ClickHouse/ClickHouse/issues/9853)

```sql
# success
SELECT count(*) /* <-- asterisk defined */
FROM numbers(4) AS n1, numbers(3) AS n2
WHERE (n1.number = n2.number);

# success
SELECT count() /* not asterisk */
FROM numbers(4) AS n1, numbers(3) AS n2, numbers(6) AS n3
WHERE (n1.number = n2.number) AND (n2.number = n3.number);

# fail
SELECT count(*) /* <-- asterisk defined */
FROM numbers(4) AS n1, numbers(3) AS n2, numbers(6) AS n3
WHERE (n1.number = n2.number) AND (n2.number = n3.number);
/* Code: 48. DB::Exception: Received from localhost:9000. DB::Exception: Multiple JOIN do not support asterisks for complex queries yet. */
```

```sql
# success
SELECT n1.number
FROM numbers(4) AS n1, numbers(3) AS n2
GROUP BY n1.number
HAVING count(*) > 1;

# fail
SELECT n1.number
FROM numbers(4) AS n1, numbers(3) AS n2, numbers(7) AS n3
GROUP BY n1.number
HAVING count(*) > 1;
/* Code: 48. DB::Exception: Received from localhost:9000. DB::Exception: Multiple JOIN do not support asterisks for complex queries yet. */
```

| **Affected queries** |||
| --- | --- | --- |
| [query_6.sql](/queries/query_6.sql) | [query_69.sql](/queries/query_69.sql) | [query_96.sql](/queries/query_96.sql) |
| [query_10.sql](/queries/query_10.sql) | [query_72.sql](/queries/query_72.sql) | |
| [query_28.sql](/queries/query_28.sql) | [query_73.sql](/queries/query_73.sql) | |
| [query_34.sql](/queries/query_34.sql) | [query_88.sql](/queries/query_88.sql) | |
| [query_35.sql](/queries/query_35.sql) | [query_90.sql](/queries/query_90.sql) | |

##### 3.7.2 'Cannot refer column "x" to table'

[github issue 9855](https://github.com/ClickHouse/ClickHouse/issues/9855)

```sql
# success
SELECT count()
FROM numbers(4) AS n1, numbers(3) AS n2
WHERE n1.number > (select avg(n.number) from numbers(3) n);

# fail
SELECT count()
FROM numbers(4) AS n1, numbers(3) AS n2, numbers(6) AS n3
WHERE n1.number > (select avg(n.number) from numbers(3) n);
/* Code: 352. DB::Exception: Received from localhost:9000. DB::Exception: Cannot refer column 'n.number' to table. */
```

| **Affected queries** |
| --- |
| [query_6.sql](/queries/query_6.sql) |
| [query_16.sql](/queries/query_16.sql) |
| [query_94.sql](/queries/query_94.sql) |

##### 3.7.3 'Missing columns: "x" while processing query'

[github issue 9861](https://github.com/ClickHouse/ClickHouse/issues/9861)

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

| **Affected queries** ||
| --- | --- |
| [query_10.sql](/queries/query_10.sql) | [query_68.sql](/queries/query_68.sql) |
| [query_32.sql](/queries/query_32.sql) | [query_69.sql](/queries/query_69.sql) |
| [query_35.sql](/queries/query_35.sql) | [query_92.sql](/queries/query_92.sql) |
| [query_41.sql](/queries/query_41.sql) | |
| [query_46.sql](/queries/query_46.sql) | |

##### 3.7.4 'COMMA to CROSS JOIN rewriter is not enabled or cannot rewrite query'

[github issue 9863](https://github.com/ClickHouse/ClickHouse/issues/9863)

```sql
# success
SELECT *
FROM (
  SELECT dummy, name
  FROM system.one, system.columns) oc, system.formats;

SELECT *
FROM (
  SELECT dummy, name
  FROM system.one, system.columns, system.tables) oct; 

# fail
SELECT *
FROM (
  SELECT dummy, name
  FROM system.one, system.columns, system.tables) oct, system.formats; 
```

| **Affected queries** |
| --- |
| [query_34.sql](/queries/query_34.sql) |
| [query_61.sql](/queries/query_61.sql) |
| [query_73.sql](/queries/query_73.sql) |
| [query_79.sql](/queries/query_79.sql) |
| [query_90.sql](/queries/query_90.sql) |

##### 3.7.5 'Mix of COMMA and other JOINS is not supported'

[github issue 9864](https://github.com/ClickHouse/ClickHouse/issues/9864)

```sql
# fail
SELECT *
FROM system.tables, system.one
  LEFT OUTER JOIN system.columns ON (dummy = is_in_partition_key);
```

| **Affected queries** |
| --- |
| [query_40.sql](/queries/query_40.sql) |
| [query_93.sql](/queries/query_93.sql) |

##### 3.7.6 'Logical error: CROSS JOIN has expressions'

[github issue 9910](https://github.com/ClickHouse/ClickHouse/issues/9910)

| **Affected queries** |
| --- |
| [query_40.sql](/queries/query_40.sql) |
| [query_93.sql](/queries/query_93.sql) |


#### 3.8 'Aggregate function "x" is found inside another aggregate function in query'

[github issue 9715](https://github.com/ClickHouse/ClickHouse/issues/9715)

| **Affected queries** |
| --- |
| [query_66.sql](/queries/query_66.sql) |



### 4 Performance issue

| **Affected queries** |
| --- |
| [query_72.sql](/queries/query_72.sql) |


## References

### TPC-DS documents

[TPC-DS Tools](http://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp) or take [already downloaded](/assets/9b0e0c62-e2be-4183-9a51-de7de896b71d-tpc-ds-tool.zip)

### Others DB benchmarks

[Vertica White paper - Benchmarks Prove the Value of an Analytical Database for Big Data](https://www.vertica.com/wp-content/uploads/2017/01/Benchmarks-Prove-the-Value-of-an-Analytical-Database-for-Big-Data.pdf)
[Vertica TPC-DS benchmark performance analysis](http://bicortex.com/vertica-mpp-database-overview-and-tpc-ds-benchmark-performance-analysis-part-3/)

[tidb-bench](https://github.com/pingcap/tidb-bench)
