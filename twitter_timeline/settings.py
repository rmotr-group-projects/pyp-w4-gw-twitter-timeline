import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds145405.mlab.com'
USERNAME = 'tweetor'
PASSWORD = 'tweettweet'
PORT = 45405
DATABASE_NAME = 'twitter-clone-api'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr='tweetor',
    pwd='tweettweet',
    host='ds145405.mlab.com',
    port=45405,
    db='twitter-clone-api')
