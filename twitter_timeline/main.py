import json

from pymongo import MongoClient
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
        username = get_username(follower['user_obj_id'])
        response.append({
            'username': username,
            'uri': '/profile/{}'.format(username)
        })

    return jsonify(response)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # user_ids_followed = g.db.friendships.find({ follower_id: user_id })
    # friendship {follower_id: user_id, followed_username: request.data['username']}
    tweets = []
    #  g.db.tweets({})
    # get the tweets of all the people the user is following
    # (no need to get user's own tweets unlike actual twitter)
    # sort tweets by latest first https://docs.mongodb.com/v3.2/reference/method/cursor.sort/

    response = []

    # should work once we figure the rest out
    # for tweet in tweets:
    #     response.append({
    #         'created': python_date_to_json_string(tweet['created']),
    #         'id': str(tweet['_id'],
    #         'text': tweet['content'],
    #         'uri': '/tweet/{}'.format('TBD'),
    #         'user_id': str(tweet['user_id')
    #     })
    return jsonify(response)

def get_username(obj_id):
    user = g.db.users.find({'_id': obj_id}, {'username': 1}).next()
    username = user['username']
    # without .next(), user is a cursor. with .next(), user is a dictionary like below
    # {u'username': u'testuser2', u'_id': ObjectId('575b5c2bab63bca09af707a4')}
    return username
