# App for Daeduck Project

## start API service
  - API Server :  `python api_srv.py`

## test mssql connectivity
  - `tsql -H 192.168.86.58 -p 1433 -U admin -P admin`

## test api service
  - common format:  `[timestamp]|[sensor_id]|[location]|[camera_list]#`

  - gas: `curl -i -X GET http://localhost:9006/gas`  
  returns:  `2017-10-20 15:29:47|leak1-71|P2A_BACK|C119_C102_C102_C81`

  - fire: `curl -i -X GET http://localhost:9006/fire`  
  returns: `2017-10-18 18:02:01|F100311|P2A_1F|C95_C96_C93_C97`

  - simulate fire alarm: `http://192.168.86.24:9006/sim_fire.html`


## other notes
  - naming of leak sensor:  `leak1-10`, from mssql
  - naming of fire sensor:  `F100431`, from socket server
  - clean db every 20 minutes

## msg format

`41 06 110a0b0c3929 01 3031 3031 313030353200 50332d324620482f452332b3ebb1a4000000000000b9dfbdc5b1e20000000000000000000000000000000000b5bfc0db0000000000`
- start : `41`
- LType: `06`
- time:
`11 0a 0b 0c 39 29`==> 17 year/ 10 month/ 11 day / 12 hr / 57 min / 41 sec
- operatio status: `01`
- Panel: `30 31`=[string]=> `01` in ascii
- Sensor ID: `30 313130303532`  =[string]=> `0 110052` =[last 6 digit]=> `110052`
          
## msg format new

== message ==
4148110a1a0a3a12000130313030303030303000000000000000000000000000000000000000000000c1d6c0bdc7e2204b455900000000000000000000000000b5bfc0db0000000000

4148110a1a0a3b0c00013031303130303239310031462d412d31000000000000000000000000000000b9dfbdc5b1e20000000000000000000000000000000000b5bfc0db0000000000

4148110a1a0a3b1d00003031303130303239310031462d412d31000000000000000000000000000000b9dfbdc5b1e20000000000000000000000000000000000c7d8c1a60000000000

== message decode ==
`fire`
4148 110a1a0a3b0c 0001 3031 30313030323931 0031462d412d31000000000000000000000000000000b9dfbdc5b1e20000000000000000000000000000000000b5bfc0db0000000000
- time:  `11 0a 1a 0a 3b 0c` ==> 17 year/ 10 month/ 26 day / 10:59:12
- operatio status: `0001`  
- Panel: `3031`=[string]=> `01` in ascii
- Sensor ID: `30313030323931`  =[string]=> `0100291`

`recovery`
4148 110a1a0a3b1d 0000 3031 30313030323931 0031462d412d31000000000000000000000000000000b9dfbdc5b1e20000000000000000000000000000000000c7d8c1a60000000000
- time:  `11 0a 1a 0a 3b 1d` ==> 17 year/ 10 month/ 26 day / 10:59:29
- operatio status: `0000`  
- Panel: `3031`=[string]=> `01` in ascii
- Sensor ID: `30313030323931`  =[string]=> `0100291`

