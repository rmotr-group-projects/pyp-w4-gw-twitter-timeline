import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds139645.mlab.com'
USERNAME = 'dev'
PASSWORD = 'letsbuildasnowman'
PORT = 39645
DATABASE_NAME = 'tweet_tweet_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
