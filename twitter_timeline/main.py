import json

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask import Flask, g, jsonify

from twitter_timeline import settings
from twitter_timeline.utils import *

from datetime import datetime

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
        friend = request.get_json()['username']
    except:
        abort(400)

    friend_id = g.db.users.find_one({'username': friend})

    if friend_id is None:
        abort(400)

    if request.method == 'POST':
        g.db.friendships.insert({'user_id': user_id, 'friend_id': friend_id['_id']})
        return '', 201

    if request.method == 'DELETE':
        g.db.friendships.delete_one({'friend_id': friend_id['_id']})
        return '', 204


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):

    followers = g.db.friendships.find({'friend_id': user_id})

    followers_list = []
    for follower in followers:
        f_details = g.db.users.find_one({'_id':follower['user_id']})
        followers_list.append({'username': f_details['username'],
                               'uri': '/profile/{}'.format(f_details['username'])})

    return jsonify(followers_list)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    #print(user_id)

    friends_query = g.db.friendships.find({'user_id': user_id})
    friends = [{'user_id': f['friend_id']} for f in friends_query]

    if len(friends) == 0:
        return jsonify([]), 200

    tweets = g.db.tweets.find({"$or": friends}).sort('created',DESCENDING)
    #print(t for t in tweets)
    tweets_list = []
    for t in tweets:
        tweets_list.append({
            'created': datetime.strftime(t['created'], '%Y-%m-%dT%H:%M:%S'),
            'id': str(t['_id']),
            'text': t['content'],
            'uri': '/tweet/{}'.format(str(t['_id'])),
            'user_id': str(t['user_id'])
        })

    #print(tweets_list)

    return jsonify(tweets_list), 200


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
