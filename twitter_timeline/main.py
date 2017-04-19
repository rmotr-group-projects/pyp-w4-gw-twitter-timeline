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
    json_data = request.get_json()
    username = json_data.get('username', None)
    if not username:
        abort(400)
    actual_user = g.db.users.find_one({'_id': ObjectId(user_id)})
    want_user = g.db.users.find_one({'username': username})
    if not want_user:
        abort(400)
    want_user_id = want_user['_id']
    
    if request.method == 'POST':
        g.db.friendships.insert({'user_id':user_id, 'username': username, 'friend_id':want_user_id,})
        return '',201
    if request.method == 'DELETE':
        g.db.friendships.delete_one({'user_id':user_id,'friend_id':want_user_id})
        return '',204
        
    
def get_username(user_id):
    return g.db.users.find_one({'_id': ObjectId(user_id)})['username']

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    followers = g.db.friendships.find({'friend_id': ObjectId(user_id)})
    
    follower_list =[]
    for f in followers:
        username = get_username(f['user_id'])
        follower_list.append({'username': username, 'uri': '/profile/{}'.format(username)})
    
    return jsonify(follower_list)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    user_friends = g.db.friendships.find({'user_id':user_id})
    print(user_friends.count())
    user_id_followed = [ObjectId(f['friend_id']) for f in user_friends]
    
    if len(user_id_followed) ==0:
        return jsonify([]),200
    tweet_LIST = []
    tweets = g.db.tweets.find({'user_id':{'$in': user_id_followed}}).sort('created',DESCENDING)
    for tweet in tweets:
        tweet_LIST.append({'created': python_date_to_json_str(tweet['created']),
                            'id': str(tweet['_id']),
                            'text': tweet['content'],
                            'uri': '/tweet/{}'.format(tweet['_id']),
                            'user_id': str(tweet['user_id'])
        })
    return jsonify(tweet_LIST)

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
