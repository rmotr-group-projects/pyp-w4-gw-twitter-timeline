import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds151137.mlab.com"
USERNAME = "t_timeline"
PASSWORD = "timeline1234"
PORT = 51137
DATABASE_NAME = "twitter"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
