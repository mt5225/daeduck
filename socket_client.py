# -*- coding: utf-8 -*-
import socket
import sqlite3
import sys
import binascii
import logging
import time
import datetime
from time import gmtime, strftime
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler

# ======= create logger ==========
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('fetchdata.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# ======= global settings ========
#_HOST = '192.168.0.150'
_HOST = 'localhost'
_PORT = 4378
# all time value are in seconds
_RECV_TIMEOUT = 1 * 10
_SOCK_POLLING = _RECV_TIMEOUT + 1
_CLEAN_DB_PERIOD = 20 * 60

def get_sensor_id(msg):
    sensor_id_hex = msg[22:34]
    str_buf = ''
    for index in range(0,12,2):
        hex_str = sensor_id_hex[index:index+2]
        ascii_str = binascii.unhexlify(hex_str)
        str_buf = str_buf + ascii_str
    str_buf = 'F' + str_buf
    logger.debug("sensor id in hex: %s ==> %s" % (sensor_id_hex, str_buf))
    return str_buf

# ======= append fire alarm messages into array =======
def decode_message(buf):
    ''' decode hex message to text message array
    '''
    data = binascii.hexlify(buf)
    msg_array = []
    msg_decode = data.split('41')
    for msg in msg_decode:
        logger.debug(msg)
        if msg[:2] == '06':
            logger.warn("fire alarm message, insert into alarm database")
            msg_array.append(
                {
                    'occurrences': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                    'sensor': get_sensor_id(msg)
                }
            )
        else:
            logger.info("not a fire alarm message, ignore")
    for item in msg_array:
        logger.debug(item)
    return msg_array

# ======= save to database =======
def save_to_db(payload):
    ''' save message to db
    '''
    try:
        conn = sqlite3.connect('daeduck_fire.db')
        cur = conn.cursor()
        for item in payload:
            record = (item['occurrences'], item['sensor'])
            cur.execute("INSERT INTO alarms VALUES(?,?)", record)
        conn.commit()
    except sqlite3.Error, e:
        logging.error("Error %s:" % e.args[0])
        sys.exit(1)
    finally:
        if conn:
            conn.close()

# ======= init database =======
def init_db():
    SQL = '''
        CREATE TABLE IF NOT EXISTS alarms (
            occurrences varchar(64),
            sensor varchar(64)
        );
    '''
    with sqlite3.connect('daeduck_fire.db') as conn:
        cursor = conn.cursor()
        cursor.execute(SQL)

# ======= init database =======
def remove_old_event():
    ''' remove all events from alarms table
    '''
    logger.debug('clean old event')
    with sqlite3.connect('daeduck_fire.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE from alarms')

# ======= fetch data from socket server =======
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
                payload = decode_message(buf)
                if len(payload) > 0: save_to_db(payload)
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
   init_db()
   scheduler = BackgroundScheduler()
   start_time = datetime.datetime.now() + datetime.timedelta(0,3)
   # add clean db job
   scheduler.add_job(remove_old_event, 'interval', seconds=_CLEAN_DB_PERIOD, start_date=start_time)
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
