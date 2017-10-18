# App for Daeduck Project

## start API service
  - API Server :  `python api_srv.py`

## test mssql connectivity
  - `tsql -H 192.168.86.58 -p 1433 -U admin -P admin`

## test api service
  - gas: `curl -i -X GET http://localhost:9006/gas`
  returns:
  `leak1-06|A_1F#leak1-08|A_1F#leak1-13|`

  - fire: `curl -i -X GET http://localhost:9006/fire`
  returns:
  `2017-10-18 18:02:01|F100311|P2A_1F|C95_C96_C93_C97`


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
- Sensor ID: `30 313130303532`  =[string]=> `0 110052` =[last 6 digit]=> `110052`
          