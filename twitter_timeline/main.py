import json

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask import Flask, g, jsonify, abort

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
    if not json_data.get('username', None):
        abort(400)
    username = json_data['username']
    user_to_follow = g.db.users.find_one({'username': username})
    if not user_to_follow:
        abort(400)
    else:
        user_followed_id = user_to_follow['_id']

    # before inserting or deleting a friendship, first check that it exists. if it doesn't, abort!
    friendship = g.db.friendships.find_one({'user_obj_id': ObjectId(user_id), 'followed_obj_id': user_followed_id})

    if request.method == 'POST':
        if friendship:
            abort(400)
        else:
            g.db.friendships.insert({'user_obj_id': ObjectId(user_id), 'followed_obj_id': user_followed_id})
            return '', 201

    if request.method == 'DELETE':
        if friendship:
            g.db.friendships.delete_many({'user_obj_id': ObjectId(user_id), 'followed_obj_id': user_followed_id})
            return '', 204
        else:
            abort(400)


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    follower_list = g.db.friendships.find({ 'followed_obj_id': ObjectId(user_id) })
    response = []

    for follower in follower_list:
        username = get_user_details(follower['user_obj_id'], 'username')
        response.append({
            'username': username,
            'uri': '/profile/{}'.format(username)
        })

    return jsonify(response)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    friendships = g.db.friendships.find({'user_obj_id': ObjectId(user_id)})

    if not friendships:
        return jsonify([])

    user_ids_followed = [ f['followed_obj_id'] for f in friendships]
    tweets = g.db.tweets.find({'user_id': {'$in': user_ids_followed}}).sort('created', DESCENDING)
    response = []

    for tweet in tweets:
        tweet_id = str(tweet['_id'])
        poster_id = str(get_user_details(tweet['user_id'], '_id'))

        response.append({
            'created': python_date_to_json_str(tweet['created']),
            'id': tweet_id,
            'text': tweet['content'],
            'uri': '/tweet/{}'.format(tweet_id),
            'user_id': poster_id
        })
    return jsonify(response)

def get_user_details(obj_id, field):
    user = g.db.users.find({'_id': obj_id}, {'username': 1}).next()
    detail = user[field]
    # without .next(), user is a cursor. with .next(), user is a dictionary like below
    # {u'username': u'testuser2', u'_id': ObjectId('575b5c2bab63bca09af707a4')}
    return detail
