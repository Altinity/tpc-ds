cd v2.11.0rc2\tools

set tpl_lst_path="..\query_templates\templates.lst"
set tpl_dir="..\query_templates"
set dialect_path="..\..\clickhouse-dialect"
set result_dir="..\..\queries"

for /l %%n in (1, 1, 99) do (
  dsqgen /input %tpl_lst_path% /directory %tpl_dir% /dialect %dialect_path% /output_dir %result_dir% /scale 1 /template query%%n.tpl /verbose y
  del %result_dir%\query_%%n.sql
  ren %result_dir%\query_0.sql query_%%n.sql
  )