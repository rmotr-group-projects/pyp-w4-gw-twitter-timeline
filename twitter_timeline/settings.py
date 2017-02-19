import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds151697.mlab.com'
USERNAME = 'dbuser'
PASSWORD = 'donthackmebro'
PORT = 51697
DATABASE_NAME = "twitter-timeline"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)

#mongodb://<dbuser>:<dbpassword>@ds017155.mlab.com:17155/mydb