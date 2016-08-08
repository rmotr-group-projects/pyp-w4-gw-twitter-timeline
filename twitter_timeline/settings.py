import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds145325.mlab.com'
USERNAME = 'rmotrg2'
PASSWORD = 'rmotrg2'
PORT = 45325
DATABASE_NAME = 'twitter_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
