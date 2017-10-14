# -*- coding: utf-8 -*-
import sqlite3
import logging
from flask import Flask, jsonify
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from types import NoneType
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

@app.route('/')
def index():
    return jsonify(msg='Hello, Daeduck!'), 200

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
        app.logger.debug("no gas alarm found in mssql database")
    return msg_short, 200

def get_leak_detail(record):
   #get leak sensor id
   tmp = record[0].split('-')
   sensor_id = "leak%s-%s" % (tmp[1], tmp[0][1:])
   sensor_detail = "%s|%s" % (sensor_id, record[1][4:][:-4])
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