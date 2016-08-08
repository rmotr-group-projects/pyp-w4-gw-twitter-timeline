import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import Flask, g, Response
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


@app.route('/friendship', methods=['POST'])
@json_only
@auth_only
@get_username
def create_friendship(username = None):
    data = request.json
    if not ('username' in data and g.db.users.find_one(data)):
        abort(400)
    
    follower = username
    followee = data['username']
    
    g.db.friendships.insert({'following': followee,
                             'username': follower})

    return Response(status=201)


@app.route('/friendship', methods=['DELETE'])
@json_only
@auth_only
@get_username
def delete_friendship(username = None):
    data = request.json
    if not ('username' in data and g.db.users.find_one(data)):
        abort(401)

    follower = username        
    followee = data['username']
    
    g.db.friendships.remove({'following': followee, 'username': follower})
    return Response(status=204)


@app.route('/followers', methods=['GET'])
@auth_only
@get_username
def get_followers(username = None):

    following = g.db.friendships.find({'following': username},
                                 {'_id': 0, 'username': 1})
    resp = []
    for user in following:
        resp.append({'username': user['username'],
                     'uri': '/profile/{}'.format(user['username'])})
    
    return Response(dumps(resp), status=201, mimetype = JSON_MIME_TYPE)


@app.route('/timeline', methods=['GET'])
@auth_only
@get_username
def get_timeline(username = None):
    timeline = []
    #fetch users followed
    following = g.db.friendships.find({'username': username},
                                    {'_id': 0, 'following': 1})
    for user in following:
        # fetch each user's id
        get_user = g.db.users.find_one({'username': user['following']})
        tweets = g.db.tweets.find({'user_id': get_user['_id']})
        for tweet in tweets:
            # fetch all tweets from user
            fmt_tweet = {'created': python_date_to_json_str(tweet['created']),
                           'id': str(tweet['_id']),
                           'text': tweet['content'],
                           'user_id': str(tweet['user_id']),
                           'uri': '/tweet/{}'.format(tweet['_id'])}
            timeline.append(fmt_tweet)
    #sort everything up
    timeline = sorted(timeline, key=lambda k: k['created'])
    timeline = timeline[::-1]
    return Response(json.dumps(timeline),status=200)


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
