from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, request, jsonify

from twitter_timeline import settings
from twitter_timeline.utils import *

app = Flask(__name__)

JSON_MIME_TYPE = 'application/json'


def connect_db(db_name):
    mongo = MongoClient(settings.FULL_MONGO_HOST, j=True)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):
    if request.method == 'POST':
        data = request.get_json()
        if 'username' not in data:
            abort(400)
        new_user = g.db.users.find_one({'username': data['username']})
        if not new_user:
            abort(400)
        new_id = new_user['_id']
        g.db.friendships.update_one({'user_id': user_id}, {'$addToSet':{'friends': new_id}}, upsert = True)
        return '', 201

    elif request.method == 'DELETE':
        data = request.get_json()
        if 'username' not in data:
            abort(400)
        doomed_user = g.db.users.find_one({'username': data['username']})
        if not doomed_user:
            abort(400)
        doomed_id = doomed_user['_id']
        g.db.friendships.update_one({'user_id': user_id}, {'$pull':{'friends': doomed_id}})
        return '', 204

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    watcher_friends = g.db.friendships.find({'friends': user_id})
    watcher_ids = [watcher['user_id'] for watcher in watcher_friends]
    watchers = g.db.users.find({'_id': {'$in': watcher_ids}})
    watcher_names = sorted(watcher['username'] for watcher in watchers)
    return jsonify([{'username': username, 'uri': '/profile/{}'.format(username)} for username in watcher_names])


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # import ipdb; ipdb.set_trace()
    friend_doc = g.db.friendships.find_one({'user_id': user_id})
    friends = friend_doc['friends'] if friend_doc else []
    tweets = g.db.tweets.find({'user_id': {'$in': friends}}).sort('created', -1)
    feed = [{
        'created': "T".join(str(tweet['created']).split()),
        'id': str(tweet['_id']),
        'text': tweet['content'],
        'uri': '/tweet/{}'.format(str(tweet['_id'])),
        'user_id': str(tweet['user_id'])} for tweet in tweets]

    return jsonify(feed)

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_authorized(e):
    return '', 401
