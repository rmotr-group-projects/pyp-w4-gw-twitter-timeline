import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds015334.mlab.com"
USERNAME = "xyzhelen"
PASSWORD = "cookies5"
PORT = 15334
DATABASE_NAME = "shinythings"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
