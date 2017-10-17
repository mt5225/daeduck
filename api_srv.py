# -*- coding: utf-8 -*-
import sqlite3
import logging
from flask import Flask, jsonify
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from types import NoneType
from time import gmtime, strftime
import pandas as pd

DB_URL = 'mssql+pyodbc://admin:admin@192.168.86.58:1433/master?driver=FreeTDS'

# innit flash app and backend db connection
app = Flask(__name__, static_url_path='', static_folder='static')
# fire db (sqlite3)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///daeduck_fire.db'
# gas db (mysql)
app.config['SQLALCHEMY_BINDS'] = {
    'gas': DB_URL,
}
db = SQLAlchemy(app)

# init lookup map
_FIRE_LOOKUP = pd.read_csv('fire_building_mapping.csv', dtype={'ID': object})

@app.route('/')
def index():
    return jsonify(msg='Hello, Daeduck!'), 200

@app.route('/fire', methods=['GET'])
def fire():
    msg_array = []
    result = db.engine.execute("SELECT * FROM alarms ORDER BY ROWID")
    for row in result:
        sensor_id = row[1][1:]
        app.logger.debug("look for location info of sensor %s" % sensor_id)
        df = _FIRE_LOOKUP.loc[_FIRE_LOOKUP['ID'] == sensor_id]
        location_info = "%s_%s" % (df.iloc[0].Building, df.iloc[0].Floor)
        msg_array.append("%s|%s|%s"% (row[0], row[1], location_info))
    app.logger.debug(msg_array)
    msg_short = '#'.join(msg_array) if msg_array > 0 else ""
    return msg_short, 200

@app.route('/gas', methods=['GET'])
def gas():
    msg_array = []
    query_str = 'select POINT_NM,FILE_NM from daeduck where ALARM_YN = 1'
    engine = db.get_engine(bind='gas')
    result = engine.execute(query_str)
    for record in result:
        app.logger.debug('row = %r' % record)
        msg_array.append(get_leak_detail(record))
    msg_short = ""
    if msg_array:
        msg_short = '#'.join(msg_array)
    else:
        app.logger.debug("no gas leak alarm found in mssql database")
    return msg_short, 200

def get_leak_detail(record):
   #get leak sensor id
   tmp = record[0].split('-')
   sensor_id = "leak%s-%s" % (tmp[1], tmp[0][1:])
   occr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
   sensor_detail = "%s|%s|P2%s" % (occr, sensor_id, record[1][4:][:-4])
   return sensor_detail

if __name__ == '__main__':
    LOG_FILENAME = './daeduck_api_srv.log'
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    CORS(app)
    app.run(host='0.0.0.0', port=9006, debug=True)