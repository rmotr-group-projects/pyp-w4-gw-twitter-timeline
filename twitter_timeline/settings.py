import os
#mongodb://<dbuser>:<dbpassword>@ds163340.mlab.com:63340/timeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds163340.mlab.com'
USERNAME = 'c9_users'
PASSWORD = 'facebook1'
PORT = 63340
DATABASE_NAME = 'timeline'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
