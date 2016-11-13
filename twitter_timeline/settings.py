import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds033116.mlab.com'
USERNAME = 'seg2151'
PASSWORD = '1pythoniscool1'
PORT = '33116'
DATABASE_NAME = 'rmotr_twitter_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
