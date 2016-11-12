import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g

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
    if 'username' not in request.json:
        abort(400), 'Missing "username" in payload'

    target_user = g.db.users.find_one({'username': request.json['username']})
    if not target_user:
        abort(400), 'Trying to follow an invalid username'

    current_user = g.db.users.find_one({'_id': ObjectId(user_id)})
    if not current_user:
        abort(404)  # should not happen as we are authenticated

    query = {
        'user': current_user['_id'],
        'user_username': current_user['username'],
        'follows': target_user['_id'],
        'follows_username': target_user['username'],
    }
    if request.method == 'POST':
        # create friendship
        g.db.friendships.insert(query)
        return "", 201
    else:
        # delete friendship
        g.db.friendships.delete_one(query)
        return "", 204


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    data = [{'username': f['user_username'],
             'uri': '/profile/{}'.format(f['user_username'])}
            for f in g.db.friendships.find({'follows': ObjectId(user_id)})]
    return json.dumps(data), 200, {'Content-Type': JSON_MIME_TYPE}


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    if not g.db.users.find_one({'_id': ObjectId(user_id)}):
        abort(404)

    following = [f['follows'] for f in g.db.friendships.find({'user': ObjectId(user_id)})]

    tweets = []
    cursor = g.db.tweets.find({'user_id': {'$in': following}}).sort('created', -1)
    for tweet in cursor:
        tweets.append({
            'id': str(tweet['_id']),
            'user_id': str(tweet['user_id']),
            'created': python_date_to_json_str(tweet['created']),
            'text': tweet['content'],
            'uri': '/tweet/{}'.format(tweet['_id']),
        })
    return json.dumps(tweets), 200, {'Content-Type': JSON_MIME_TYPE}


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
