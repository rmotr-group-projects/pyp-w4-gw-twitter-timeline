# -*- coding: utf-8 -*-
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds019940.mlab.com'
USERNAME = 'rmotrtestuser'
PASSWORD = '11SleepyMonkeys'
PORT = 19940
DATABASE_NAME = 'rmotr-b6-pyp-g1-phil-patrick-twitter'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
