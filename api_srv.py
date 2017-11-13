# -*- coding: utf-8 -*-
import logging
import sys
from flask import Flask, jsonify
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from types import NoneType
from datetime import datetime, timedelta
import pandas as pd

#DB_URL = 'mssql+pyodbc://admin:admin@192.168.86.58:1433/master?driver=FreeTDS'
DB_URL = 'mssql+pyodbc://cctv:1qaz2wsx!@#$@192.168.6.101:1433/DDEMS?driver=SQL+Server+Native+Client+11.0'
#MYSQL_DB_URL = 'mysql+mysqldb://root:root@192.168.33.10/daeduck_alarm_momoda'
MYSQL_DB_URL = 'mysql+mysqldb://root:1234@192.168.236.1/daeduck_alarm_momoda'
DUMMY_FIRE = 'F99999'

# innit flash app and backend db connection
app = Flask(__name__, static_url_path='', static_folder='static')
# gas db (mysql)
app.config['SQLALCHEMY_BINDS'] = {
    'gas': DB_URL,
    'fire': MYSQL_DB_URL
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

_DB = SQLAlchemy(app)

# init lookup map
_FIRE_LOOKUP = pd.read_csv('fire_building_mapping.csv', dtype={'ID': object})
_FIRE_CCTV_LOOKUP = pd.read_csv('fire_cctv_mapping.csv', dtype={'ID': object})
_GAS_CCTV_LOOKUP = pd.read_csv('gas_cctv_mapping.csv', dtype={'ID': object})

@app.route('/')
def index():
    return jsonify(msg='Hello, Daeduck!'), 200

@app.route('/command/<status>', methods=['GET'])
def dummy_fire(status):
    ''' create a test fire alarm
    '''
    occr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    engine = _DB.get_engine(bind='fire')
    engine.execute("INSERT INTO fire_alarms (occurrences,sensor,status) VALUES ('%s', '%s', '%s')" % (occr, DUMMY_FIRE, status))
    return status, 200


@app.route('/fire', methods=['GET'])
def fire():
    msg_array = []
    engine = _DB.get_engine(bind='fire')
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    result = engine.execute("SELECT occurrences,sensor,status FROM fire_alarms where locate('%s', occurrences)>0 OR locate('%s', occurrences)>0" % (today_str, yesterday_str))
    for row in result:
        # remove letter F from sensor id
        sensor_id = row[1][1:]
        app.logger.debug("look for location info of fire sensor %s" % sensor_id)
        # get floor and building info
        location_df = _FIRE_LOOKUP.loc[_FIRE_LOOKUP['ID'] == sensor_id]
        cctv_df = _FIRE_CCTV_LOOKUP.loc[_FIRE_CCTV_LOOKUP['ID'] == sensor_id]
        if len(location_df.index > 0) and len(cctv_df.index > 0):
            location_info = "%s_%s" % (location_df.iloc[0].Building, location_df.iloc[0].Floor)
            cctv_info = "%s_%s_%s_%s" % (cctv_df.iloc[0].CCTV1, cctv_df.iloc[0].CCTV2, cctv_df.iloc[0].CCTV3,cctv_df.iloc[0].CCTV4)
            status = row[2]
            msg_array.append("%s|%s|%s|%s|%s"% (row[0], row[1], location_info, cctv_info, status))
    app.logger.debug(msg_array)
    msg_short = '#'.join(msg_array) if msg_array > 0 else ""
    return msg_short, 200

@app.route('/gas', methods=['GET'])
def gas():
    msg_array = []
    query_str = "select POINT_NM,FILE_NM,CURR_DT from UVW_POINTINFO_for_cctv where ALARM_YN = 1 ORDER BY CURR_DT desc"
    engine = _DB.get_engine(bind='gas')
    result = engine.execute(query_str)
    for record in result:
        app.logger.debug('row = %r' % record)
        sensor_detail = get_leak_detail(record)
        if sensor_detail is not "":
            msg_array.append(sensor_detail) 
    msg_short = ""
    if msg_array:
        msg_short = '#'.join(msg_array)
    else:
        app.logger.debug("no gas leak alarm found in mssql database")
    return msg_short, 200

def get_leak_detail(record):
    # get leak sensor id
    tmp = record[0].split('-')
    second = tmp[0][2] if tmp[0][:2] == '00' else tmp[0][1:].strip()  
    sensor_id = "leak%s-%s" % (tmp[1].strip(), second)
    app.logger.debug('sensor_id = %s' % sensor_id)
    occr = record[2][:-4]
    # get location info
    location_info = "P2%s" %  record[1][4:][:-4]
    # get cctv info
    sensor_id_lookup = "%s-%s" % (tmp[1].strip(), second)
    app.logger.debug('sensor_lookup_id = %s' % sensor_id_lookup)
    df = _GAS_CCTV_LOOKUP.loc[_GAS_CCTV_LOOKUP['ID'] == sensor_id_lookup]
    sensor_detail = ""
    if len(df.index > 0):
        cctv_info = "%s_%s_%s_%s" % (df.iloc[0].CCTV1, df.iloc[0].CCTV2, df.iloc[0].CCTV3,df.iloc[0].CCTV4)
        sensor_detail = "%s|%s|%s|%s" % (occr, sensor_id,location_info, cctv_info)
        app.logger.debug(sensor_detail)
    return sensor_detail

if __name__ == '__main__':
    LOG_FILENAME = './daeduck_api_srv.log'
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    #handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    CORS(app)
    app.run(host='0.0.0.0', port=9006, debug=True, threaded=True)
