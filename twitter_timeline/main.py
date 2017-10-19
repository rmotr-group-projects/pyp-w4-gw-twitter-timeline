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
    data = request.get_json()
    try:
        username = data['username']
    except KeyError:
        return '', 400
    user = g.db.users.find_one({'username': username})
    if user:
        if request.method == 'POST':
            g.db.friendships.insert_one(
                {'user_id': user_id, 'following': user['_id']})
            return '', 201

        if request.method == 'DELETE':
            g.db.friendships.delete_one(
                {'user_id': user_id, 'following': user['_id']})
            return '', 204
    return '', 400


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    # returns list of users following auth_user
    # dict of username and URI

    follower_list = g.db.friendships.find({"following": ObjectId(user_id)})
    response = []

    for follower in follower_list:
        user = g.db.users.find_one({'_id': ObjectId(follower['user_id'])})
        username = user['username']
        response.append({
            'username': username,
            'uri': '/profile/{}'.format(username)
        })

    return jsonify(response)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # gets list of tweets from from users that auth_user follows
    # sorted from newest to oldest
    # get all ids user is following
    # {'user_id': user_id, 'following': user['_id']
    #     ^ us                  ^ them
    follower_list = g.db.friendships.find({"user_id": user_id})
    all_ids_list = [ObjectId(f['following']) for f in follower_list]

    if len(all_ids_list) == 0:
        return jsonify([]), 200

    # get user's tweets
    all_tweets = g.db.tweets.find({'user_id': {'$in': all_ids_list}}).sort(
        'created', DESCENDING)

    all_tweets_list = []
    for tweet in all_tweets:
        all_tweets_list.append(
            {
                'created': datetime.strftime(tweet['created'],
                                             '%Y-%m-%dT%H:%M:%S'),
                'id': str(tweet['_id']),
                'text': tweet['content'],
                'uri': '/tweet/{}'.format(str(tweet['_id'])),
                'user_id': str(tweet['user_id'])

            })

    return jsonify(all_tweets_list), 200


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401

# mongo commands
# cursor = db.restaurants.find()  <- returns all documents in collection

# The following operation finds documents whose borough field equals "Manhattan".
#   cursor = db.restaurants.find({"borough": "Manhattan"})
