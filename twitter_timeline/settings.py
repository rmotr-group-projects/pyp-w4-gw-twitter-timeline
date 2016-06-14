import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# account pyp-w4-gw-twitter-timeline
HOST = 'ds025973.mlab.com'
USERNAME = 'pyp-w4-gw-twitter-timeline'
PASSWORD = 'rmotr-G1'
PORT = 25973
DATABASE_NAME = 'pyp-w4-gw-twitter-timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
