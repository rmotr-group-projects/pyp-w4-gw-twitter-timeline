import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds163360.mlab.com'
USERNAME = 'ffv'
PASSWORD = 'rmotr1234'
PORT = 63360
DATABASE_NAME = 'twitter-db'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
