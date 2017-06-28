import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# mongodb://twitter-timeline1:timeline123@ds139242.mlab.com:39242/twitter-timeline

# % mongo ds139242.mlab.com:39242/twitter-timeline -u twitter-timeline1 -p timeline123

HOST = "ds139242.mlab.com"
USERNAME = "twitter-timeline1"   
PASSWORD = "timeline123"
PORT = 39242
DATABASE_NAME = "twitter-timeline"

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD, 
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
