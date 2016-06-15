import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'ds015334.mlab.com'
USERNAME = 'akshith'        #database user
PASSWORD = 'akshith'        
PORT = 15334
DATABASE_NAME = 'rmotr-g3-batch-6'

# mongodb://<dbuser>:<dbpassword>@ds015334.mlab.com:15334/rmotr-g3-batch-6


FULL_MONGO_HOST = "mongodb://{usr}:{pwd}@{host}:{port}/{db}".format(
    usr=USERNAME,
    pwd=PASSWORD,
    host=HOST,
    port=PORT,
    db=DATABASE_NAME)
