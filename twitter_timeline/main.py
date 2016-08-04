import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, Response
import datetime
from twitter_timeline import settings
from twitter_timeline.utils import *

JSON_MIME_TYPE = "application/json"

app = Flask(__name__)
JSON_MIME_TYPE = 'application/json'
#First have to figure out authentication in headers - #auth_token = request.headers.get("Authorization")
#in database (MongoDB) need to probably have 4 tables:
#user, authentication(to see who is logged in), tweets(to hold tweets)
#for friendshp table, have a user, and who they are following
#the friendship collection should contain the username of account owners, and a list of their follower usernames, and their uris
#for the timeline view, should perform get request on tweets of each user in the list of following

# database_name.collection_name.insert_one/many(dictionaryobject?)
def connect_db(db_name):
    mongo = MongoClient(settings.FULL_MONGO_HOST)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


@app.route('/friendship', methods=['POST', 'DELETE'])
#@json_only
@auth_only
def friendship(user_id):
    #Checking if there's a username in our request
    try:
        #
        friend_username = request.json["username"]
        friend_object = g.db.users.find_one({"username": friend_username})
        friend_id = friend_object["_id"]
        user_object = g.db.users.find_one({"_id": user_id})
    except:
        print("ERROR: NO USERNAME IN PAYLOAD. NO USERNAME IN DATABASE")
        abort(400)
    
    #check if user is attempting to follow himself/herself
    if user_id == friend_id:
        #print (user_id, friend_id)
        abort(401)
        
    #create a set called following for the user object if it doesn't already exist 
    followING = user_object.setdefault("following", [])
    followERS = friend_object.setdefault("followers", []) #ripping off code yolo 
    
    if request.method == 'POST':
        """updates following list for user, and followers list for the followed friend"""
        
        #this will test if we're already following that friend. spit out 400 code if we're already following. 
        #it will also test if we're already in the followERS
        if (friend_object["_id"] not in followING) and (user_object["_id"] not in followERS):
            followING.append(friend_object["_id"])
            followERS.append(user_object['_id']) 
            g.db.users.update_one( {"_id": ObjectId(user_id)}, {"$set": {"following": followING}} )
            g.db.users.update_one( {"_id": ObjectId(friend_object["_id"])}, {"$set": {"followers": followERS}} )
            return Response(status=201)
        else:
            abort(400)
    if request.method == "DELETE":
        #this will test if we're following the friend, before unfollowing
        if (friend_object["_id"] in followING) and (user_object["_id"] in followERS): #need to add followERS stuff here too
            followING.remove(friend_object["_id"])
            followERS.remove(user_object["_id"])
            g.db.users.update_one( {"_id": ObjectId(user_id)}, {"$set": {"following": followING}} )
            g.db.users.update_one( {"_id": ObjectId(friend_object["_id"])}, {"$set": {"followers": followERS}} )
            return Response(status=204)
        else:
            abort(400)
    
@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    follower_id_list = _get_user_followers(user_id)
    followers_return = []
    for _id in follower_id_list:
        follower_object = g.db.users.find_one({"_id": _id})
        
        temp_dict = {}
        temp_dict['username'] = follower_object["username"]
        temp_dict['uri'] = "/profile/{username}".format(username = temp_dict['username'])
        followers_return.append(temp_dict)
        #add to list "followers_return" a dictionary containing the _id's username and uri
    response = Response(response = json.dumps(followers_return), status = 201, mimetype = JSON_MIME_TYPE)
    
    return response

#first ima try to add followers list
@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    following = _get_user_following(user_id)
    timeline = []
    all_unsorted_tweets = []
    for _id in following:
        tweets = g.db.tweets.find({"user_id": _id})
        for tweet in tweets:
            temp_dict = {}
            temp_dict['created'] = tweet['created']
            temp_dict['id'] = tweet['_id']
            temp_dict['text'] = tweet['content']
            temp_dict['uri'] = "/tweet/{tweet_id}".format(tweet_id = tweet['_id'])
            temp_dict['user_id'] = _id
            all_unsorted_tweets.append(temp_dict)
    # timeline = sorted(all_unsorted_tweets, key = _date_sorting, reverse = True)
    #look at utils
    
    return str(all_unsorted_tweets)
    #return str(timeline)

# def sqlite_date_to_python(date_str):
#     return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


# def python_date_to_json_str(dt):
#     return dt.strftime("%Y-%m-%dT%H:%M:%S")
#     "created": {
#         "$date": "2016-06-11T12:00:00.000Z"

# def _date_sorting(tweet_info):
#     date = sqlite_date_to_python(str(tweet_info['created']))
#     #looks like "2016"
#     # date = datetime(date)
#     return date


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401

def _get_user_followers(user_id):
    user_object = g.db.users.find_one({"_id": user_id})
    user_object.setdefault("followers", [])
    return user_object["followers"]
   
def _get_user_following(user_id):
    user_object = g.db.users.find_one({"_id": user_id})
    user_object.setdefault("following", [])
    return user_object["following"]
  