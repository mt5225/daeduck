# App for Daeduck Project

## start API service
  - API Server :  `python api_srv.py`

## test mssql connectivity
  - `tsql -H 192.168.86.58 -p 1433 -U admin -P admin`

## test api service
  - for gas: `curl -i -X GET http://localhost:9006/gas`
  returns:
  `leak1-06|A_1F#leak1-08|A_1F#leak1-13|`



## other notes
  - naming of leak sensor:  `leak1-10`, from mssql
  - name of fire sensor:  `F100431`, from socket server

## msg format

`41 06 110a0b0c3929 01 3031 3031 313030353200 50332d324620482f452332b3ebb1a4000000000000b9dfbdc5b1e20000000000000000000000000000000000b5bfc0db0000000000`
- start : `41`
- LType: `06`
- time:
`11 0a 0b 0c 39 29`==> 17 year/ 10 month/ 11 day / 12 hr / 57 min / 41 sec
- operatio status: `01`
- Panel: `30 31`=[string]=> `01` in ascii
- Sensor ID: `30 31 313030353200`  =[string]=> `01 100520` =[last 6 digit]=> `100520`

41 05 110a0b0c3929 0030313030303030303000000000000000000000000000000000000000000000c1d6c0bdc7e2204b455900000000000000000000000000c7d8c1a60000000000
          