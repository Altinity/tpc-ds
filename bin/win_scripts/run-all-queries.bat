for /r %%i in (queries\*.sql) do (
  docker exec -it clickhouse-server clickhouse-client -mn | %%i
  echo TODO
  goto :eof
  )