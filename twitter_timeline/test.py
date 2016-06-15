from pymongo import MongoClient
from settings import *

mongo = MongoClient(FULL_MONGO_HOST)
db = mongo.DATABASE_NAME

friend_name ="dave"
friend_dict = friend_dict = {"username": friend_name ,"uri": "/profile/" + friend_name}  

db.users.update_one(
        { "username": "testuser1"},
        { 
            "$push": { "friends": friend_dict } 
        }
    )


