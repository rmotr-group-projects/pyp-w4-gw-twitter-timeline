import json

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask import Flask, g, request, jsonify

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


@app.route('/friendship', methods=['POST', 'DELETE']) #friendship/username?user_id=token_
@json_only
@auth_only
def friendship(user_id):
    json_data = request.get_json()
    if not json_data.get('username',None):
        abort(400)
    
    user_to_follow = g.db.users.find_one({'username':json_data['username']})
    if not user_to_follow:
        abort(400)
    else:
        following_id = user_to_follow['_id']
  
        
    if request.method == "POST": #testuser1 follows testuser2
        g.db.friendships.insert_one({'user_id': user_id ,'friend_id': following_id})
        return '',201
    
    if request.method == "DELETE":
        # delete user from friendship collection
        g.db.friendships.delete_many({'user_id': user_id ,'friend_id': following_id})
        return '',204


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id): 
    friends = g.db.friendships.find({'friend_id':ObjectId(user_id)})
    followers = []
    #testuser1 follows testuser2
    #testuser3 follows testuser2

    for f in friends:
        user = g.db.users.find_one({'_id':ObjectId(f['user_id'])})
        username = user['username']
        followers.append({'username':username,'uri':'/profile/{}'.format(username)})
    
    return jsonify(followers)

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    friends = g.db.friendships.find({'user_id':user_id})
    friends_ids = []
    
    for f in friends:
        friends_ids.append(ObjectId(f['friend_id']))
        
    tweets = g.db.tweets.find({'user_id': {'$in': friends_ids} }).sort('created',DESCENDING)
    output = []
    
    for t in tweets:
        
        output.append({
            'created': python_date_to_json_str(t['created']),
            'id': str(t['_id']),
            'text': t['content'],
            'uri': '/tweet/{}'.format(t['_id']),
            'user_id': str(t['user_id'])
        })
    
    return jsonify(output)


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401