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


@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
@get_own_user
def create_friendship(own_user = None):
    data = request.json
    if not ('username' in data and g.db.users.find_one(data)):
        abort(400)
    followee = data['username']
    if request.method == 'POST':
        g.db[own_user].insert({'status': 'follows', 'username': followee,
                           'uri': '/profile/{}'.format(followee)})
        g.db[followee].insert({'status': 'followed', 'username': own_user,
                           'uri': '/profile/{}'.format(own_user)})
        return Response(status=201)
    elif request.method == 'DELETE':
        g.db[own_user].remove({'status': 'follows', 'username': followee})
        g.db[followee].remove({'status': 'followed', 'username': own_user})
        return Response(status=204)

# @app.route('/friendship', methods=['DELETE'])
# @json_only
# @auth_only
# @get_own_user
# def delete_friendship(own_user = None):
#     data = request.json
#     if not ('username' in data and g.db.users.find_one(data)):
#         abort(401)
#     followee = data['username']
    


@app.route('/followers', methods=['GET'])
@auth_only
@get_own_user
def own_users(own_user = None):

    resp = g.db[own_user].find({'status': 'followed'}, {'_id': 0, 'status': 0})
    
    return Response(dumps(resp), status=201, mimetype = JSON_MIME_TYPE)


@app.route('/timeline', methods=['GET'])
@auth_only
@get_own_user
def get_timeline(own_user = None):
    timeline = []
    following = g.db[own_user].find({'status': 'follows'},
                                    {'_id': 0, 'username': 1})
    for user in following:
        # fetch each user's id
        user_id = g.db.users.find_one({'username': user['username']})
        tweets = g.db.tweets.find({'user_id': user_id['_id']})
        for tweet in tweets:
            # fetch all tweets from user
            fmt_tweet = {'created': python_date_to_json_str(tweet['created']),
                           'id': str(tweet['_id']),
                           'text': tweet['content'],
                           'user_id': str(tweet['user_id']),
                           'uri': '/tweet/{}'.format(tweet['_id'])}
            timeline.append(fmt_tweet)
    timeline = sorted(timeline, key=lambda k: k['created'], reverse = True)
    return Response(json.dumps(timeline),status=200)

