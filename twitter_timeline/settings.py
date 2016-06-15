import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds019970.mlab.com"
USERNAME = "philipp"
PASSWORD = "password"
PORT = 19970
DATABASE_NAME = "twitter-timeline"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)

print FULL_MONGO_HOST