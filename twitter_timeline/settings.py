import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds044679.mlab.com'
USERNAME = 'aronivars'
PASSWORD = 'bigron86'
PORT = 44679
DATABASE_NAME = 'twitter_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
