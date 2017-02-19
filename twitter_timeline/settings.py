import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = "ds151917.mlab.com"
USERNAME = "seg2151"
PASSWORD = "password1"
PORT = 51917
DATABASE_NAME = "twitter_timeline"

# HOST = 'ds033116.mlab.com'
# USERNAME = 'test_user'
# PASSWORD = 'password1'
# PORT = 33116
# DATABASE_NAME = 'twitter_test_db'

FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
