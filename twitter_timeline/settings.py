import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds033076.mlab.com'
USERNAME = 'nekatak'
PASSWORD = 'f31256789'
PORT = 33076
DATABASE_NAME = 'twitter_timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)

#mongodb://<dbuser>:<dbpassword>@ds033076.mlab.com:33076/twitter_timeline
