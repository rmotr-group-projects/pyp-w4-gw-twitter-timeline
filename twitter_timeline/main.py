import json
import collections
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, jsonify
from datetime import datetime
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
    body = request.json
    if 'username' not in body:
        abort(400)

    friend = g.db.users.find_one({"username":body['username']})
    
    if not friend:
        abort(400)
    if request.method == 'POST':
        g.db.friendships.insert({"user_id": ObjectId(user_id), 
                                "friend_id": ObjectId(friend['_id'])})
    friend = g.db.users.find_one({"username": body['username']})

    if not friend:
        abort(400)
    if request.method == 'POST':
        g.db.friendships.insert({"user_id": ObjectId(user_id),
                                 "friend_id": ObjectId(friend['_id'])})
        return '', 201
    if request.method == 'DELETE':
        g.db.friendships.remove({"user_id": user_id, "friend_id": friend['_id']})
        return '', 204

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    response = []
    friends = g.db.friendships.find({"friend_id": user_id})
    for friend in friends:
        friend_info = g.db.users.find_one({"_id": friend['user_id']})
        friendship = {"username": friend_info['username'], 
                      "uri": "/profile/{}".format(friend_info['username'])}
        response.append(friendship)
    return jsonify(response), 200
    
        friendship = {"username": friend_info['username'],
                      "uri": "/profile/{}".format(friend_info['username'])}
        response.append(friendship)
    return jsonify(response), 200

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    response = []
    friends = g.db.friendships.find({"user_id": user_id})
    for friend in friends:
        tweets = g.db.tweets.find({"user_id": friend['friend_id']})
        for tweet in tweets:
            tweet_data = {'created': tweet['created'],
                          'id': str(tweet['_id']),
                          'text': tweet['content'],
                          'uri': '/tweet/{}'.format(tweet['_id']),
                          'user_id': str(friend['friend_id'])
                         }
            response.append(tweet_data)
    response.sort(key = lambda i: i['created'], reverse=True)
    for item in response:
        item['created'] = python_date_to_json_str(item['created'])
    return jsonify(response), 200
                          }
            response.append(tweet_data)
    response.sort(key=lambda i: i['created'], reverse=True)
    for item in response:
        item['created'] = python_date_to_json_str(item['created'])
    return jsonify(response), 200
    
@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
