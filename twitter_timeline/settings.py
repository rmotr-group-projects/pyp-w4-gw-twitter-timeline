import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds033036.mlab.com"
USERNAME = "pkkondamuri"
PASSWORD = "Rmotr_project1"
PORT = 33036#13014
DATABASE_NAME = "kondamuri_db"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
