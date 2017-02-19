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
    friendships = g.db.friendships
    json_data = request.get_json()
    if not json_data.get('username', None):
        abort(400)
    followed = g.db.users.find_one({'username': json_data['username']})
    if not followed:
        abort(400)
    else:
        follow_id = followed['_id']
    f = friendships.find_one({'user': user_id, 'follows': follow_id})
    if request.method == 'POST':
        if not f:
            f = friendships.insert_one({'user': user_id, 'follows': follow_id})
            return '', 201
    
    if request.method == 'DELETE':
        g.db.friendships.delete_many({'user': user_id, 'follows': follow_id})
        return '', 204
 


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    friendships = g.db.friendships.find({'follows': ObjectId(user_id)})
    follower_list = []
    for f in friendships:
        follower_name = get_user_name(f['user'])
        follower_list.append(dict(username=follower_name,
                                  uri='/profile/{}'.format(follower_name)))
    return jsonify(follower_list)
    
    
@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    following = g.db.friendships.find({'user': user_id})
    f_ids = []
    for f in following:
        f_ids.append(ObjectId(f['follows']))
    tweets = g.db.tweets.find({'user_id': {'$in': f_ids}}) \
        .sort('created', DESCENDING)
    json_output = []
    for t in tweets:
        json_output.append(dict(created = python_date_to_json_str(t['created']),
                                id = str(t['_id']),
                                text = t['content'],
                                uri = '/tweet/{}'.format(t['_id']),
                                user_id = str(t['user_id'])))
    return jsonify(json_output)


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
