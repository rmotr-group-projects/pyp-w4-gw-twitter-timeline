import json

from pymongo import MongoClient, DESCENDING
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
    request_json = request.get_json()

    if 'username' not in request_json:
        abort(400) #passed username doesnt exist
    
    cursor = g.db.users.find_one({'username': request_json['username']})
    
    if cursor is None:
        abort(400)
    
    if request.method == 'POST':
        g.db.friendships.update(
                {'user_id': user_id},
                {'$push': {
                    'following': {'username': request_json['username'], 'uri': '/profile/{}'.format(request_json['username'])}
                }
            }, upsert=True)
        
        return '', 201
        
    if request.method == 'DELETE':
        g.db.friendships.update(
                {'user_id': user_id},
                {'$pull': {
                    'following': {'username': request_json['username'], 'uri': '/profile/{}'.format(request_json['username'])}
                }
            })
            
        return '', 204

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    profile = g.db.users.find_one({'_id': user_id})
    cursor = g.db.friendships.find({"following.username": "{}".format(profile['username'])})
    
    followers = []
    
    for follower in cursor:
        follow_user = g.db.users.find_one({'_id': follower['user_id']})
        followers.append({'username': follow_user['username'], 'uri': '/profile/{}'.format(follow_user['username'])})
        
    return json.dumps(followers), 201

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    user_friendships = g.db.friendships.find_one({'user_id': user_id})
    
    following = []
    
    if user_friendships is None:
        return json.dumps(following)
    
    for person in user_friendships['following']:
        followed_profile = g.db.users.find_one({'username': person['username']})
        following.append(followed_profile['_id'])
    
    cursor = g.db.tweets.find({"user_id": {"$in": following}}, sort=[('created', DESCENDING)])
    
    timeline = []
    
    for tweet in cursor:
        timeline.append({
            'created': python_date_to_json_str(tweet['created']),
            'id': str(tweet['_id']),
            'text': tweet['content'],
            'uri':  '/tweet/{}'.format(str(tweet['_id'])),
            'user_id': str(tweet['user_id']),
        })
    
    return json.dumps(timeline)

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
