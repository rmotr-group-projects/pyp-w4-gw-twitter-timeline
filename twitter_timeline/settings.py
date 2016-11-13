import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds151697.mlab.com'
USERNAME = 'kiobst'
PASSWORD = 'password'
PORT = 51697
DATABASE_NAME = 'rmotr_twitter_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
