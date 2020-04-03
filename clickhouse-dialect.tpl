define _BEGIN = "USE tpcds; SET partial_merge_join = 1, partial_merge_join_optimizations = 1, max_bytes_before_external_group_by = 5000000000, max_bytes_before_external_sort = 5000000000;";
define __LIMITA = "";
define __LIMITB = "";
define __LIMITC = "LIMIT %d";
define _END = "";
