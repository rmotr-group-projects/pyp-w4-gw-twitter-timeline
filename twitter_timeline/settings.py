import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds145295.mlab.com"
USERNAME = "corez"
PASSWORD = "monkey"
PORT = "45295"
DATABASE_NAME = "corez"
#mongodb://<dbuser>:<dbpassword>@ds145295.mlab.com:45295/corez
FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
