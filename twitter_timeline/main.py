import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, Response
import datetime
from twitter_timeline import settings
from twitter_timeline.utils import *

app = Flask(__name__)
JSON_MIME_TYPE = 'application/json'

def connect_db(db_name):
    mongo = MongoClient(settings.FULL_MONGO_HOST)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
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
        abort(400)
    
    #check if user is attempting to follow himself/herself
    if user_id == friend_object["_id"]:
       abort(401)
        
    #create a set called following for the user object if it doesn't already exist 
    followING = user_object.setdefault("following", [])
    followERS = friend_object.setdefault("followers", []) 
    
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
        followers_return.append({'username': follower_object["username"],
                                 'uri': "/profile/{}".format(follower_object["username"])
                                })        
    return Response(response = json.dumps(followers_return), status = 201, mimetype = JSON_MIME_TYPE)

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    following = _get_user_following(user_id)
    all_unsorted_tweets = []
    for _id in following:
        tweets = g.db.tweets.find({"user_id": _id})
        for tweet in tweets:
            all_unsorted_tweets.append({'created': sqlite_date_to_python(str(tweet['created'])),
                                        'id':      str(tweet['_id']),
                                        'text':    tweet['content'],
                                        'uri':     "/tweet/{}".format(tweet['_id']),
                                        'user_id': str(_id)
                                        })            
    timeline = sorted(all_unsorted_tweets, key = lambda x: x["created"], reverse = True)
    for tweet in timeline:
        tweet['created'] = python_date_to_json_str(tweet['created'])
    return Response(response = json.dumps(timeline), status = 200, mimetype= JSON_MIME_TYPE)
            

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401

def _get_user_followers(user_id):
    user_object = g.db.users.find_one({"_id": user_id})
    return user_object.setdefault("followers", [])
   
def _get_user_following(user_id):
    user_object = g.db.users.find_one({"_id": user_id})
    return user_object.setdefault("following", [])
    
  