import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, request

from twitter_timeline import settings
from twitter_timeline.utils import *

import settings

app = Flask(__name__)

JSON_MIME_TYPE = 'application/json'


def connect_db(db_name = settings.DATABASE_NAME):
    mongo = MongoClient(settings.FULL_MONGO_HOST)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):
    if not "username" in request.data.json(): return abort(400) #Error if no target user was passed
    #get target user, verify if exists
    target_user = g.db.users.find_one({"username": request["username"]})
    if not target_user:
        return abort(404) #Error if target user doesnt exist
    else:
        target_user = target_user["user_id"]

        #if post, follow
        if request.method == 'POST':
            #include ourselves inside target follower list
            g.db.friendships.update(
                { "user_id": target_user },
                { "$addToSet": {"followers": [user_id] } }
            )
            return Response("", 201)
            
        #if delete, unfollow
        elif request.method == 'DELETE':
            g.db.friendships.delete(
                {"user_id": target_user},
                {"$pullAll":{"followers": [user_id] } }
            )
            return Response("", 204)
        



@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    user = g.db.friendships.find_one({"user_id": user_id})
    followers = user["followers"]
    return json.dumps(followers)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    tweets = []
    friendship = g.db.friendships.find_one({"user_id": user_id})
    for follower in frienship["followers"]:
        tweets += g.db.tweets.find({"user_id": follower})

    return sorted(tweets, key=lambda k: k['created'])

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
