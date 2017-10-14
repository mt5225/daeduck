# App for Daeduck Project

## start API service
  - API Server :  `python api_srv.py`

## test mssql connectivity
  - tsql -H 192.168.86.58 -p 1433 -U admin -P admin

## test api service
  - for gas: `curl -i -X GET http://localhost:9006/gas`