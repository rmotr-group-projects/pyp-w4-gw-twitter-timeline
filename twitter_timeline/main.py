import json

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask import Flask, g, jsonify

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

    try:
        friend = g.db.users.find_one({'username': request.json['username']})['username']
        user = g.db.users.find_one({'_id': ObjectId(user_id)})['username']
    except:
        abort(400)
    
    if request.method == "POST":
        f = g.db.friendships.insert_one({"user": user, "follows": friend})
        return '', 201
    
    if request.method == "DELETE":
        g.db.friendships.delete_many({"user": user, "follows": friend})
        return '', 204


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    
    try:
        user = g.db.users.find_one({'_id': ObjectId(user_id)})['username']
        followers = g.db.friendships.find({"follows": user})
    except:
        abort(400)
    
    json_list = []
    
    for follower in followers:
        json_list.append(dict(username=str(follower['user']), uri='/profile/{}'.format(str(follower['user']))))

    return jsonify(json_list), 200


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    
    try:
        user = g.db.users.find_one({"_id": ObjectId(user_id)})['username']
        follows = [follower['follows'] for follower in g.db.friendships.find({"user": user})]
        list_of_follower_ids = [g.db.users.find_one({'username': f})['_id'] for f in follows]
    except:
        abort(400)
    
    tweets = g.db.tweets.find({'user_id': {'$in': list_of_follower_ids}}).sort('created', DESCENDING)

    
    json_list = []
    for tweet in tweets:
        json_list.append(dict(
            created = str(tweet['created']),
            id = str(tweet['_id']),
            text = str(tweet['content']),
            uri = '/tweet/{}'.format(str(tweet['_id'])),
            user_id = str(tweet['user_id'])
        ))
    
    return jsonify(json_list), 200
    

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
