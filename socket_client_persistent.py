# client.py  
import socket
import logging
import binascii
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from logging.handlers import RotatingFileHandler


# create logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('fetchdata.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# global settings
#_HOST = '192.168.0.150'
_HOST = 'localhost'
_PORT = 4378
# all time value are in seconds
_RECV_TIMEOUT = 1 * 60
_SOCK_POLLING = _RECV_TIMEOUT + 1

def fetch_data():
    ''' fetch data from socket server
    '''
    # create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((_HOST, _PORT))                               
    s.settimeout(_RECV_TIMEOUT)
    try:
        while True:
            buf = s.recv(1024)
            if len(buf) > 1:
                data = binascii.hexlify(buf)
                logger.debug(data)
            else:
                logger.debug("received %d bytes, server sokect closed" % len(buf))
                s.close()
                break
    except socket.timeout as err:
        logger.debug(err)
    finally:	
        s.close()

if __name__ == '__main__':
   ''' argument: clearn up event db in N minutes
   '''
   scheduler = BackgroundScheduler()
   start_time = datetime.datetime.now() + datetime.timedelta(0,3)
   # add fetch data job
   scheduler.add_job(fetch_data, 'interval', seconds=_SOCK_POLLING, start_date=start_time)
   # start job scheduler
   scheduler.start()
   try:
       while True:
           time.sleep(2)
   except (KeyboardInterrupt, SystemExit):
       # Not strictly necessary if daemonic mode is enabled but should be done if possible
       scheduler.shutdown()