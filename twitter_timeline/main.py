import json

from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask import Flask, g, request, jsonify, make_response, abort
import datetime

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
    # assume friendship table looks like this:
    # {'user_id': <user_1>, 'following_ids': [<user_2>, <user_3>,...]}
    # {'user_id': <base_user>, 'follows': <target_user>}
    # {'user_id': <base_user>, 'follows': <target_user2>}
    # {'user_id': <base_user2>, 'follows': <target_user>}
    
    
    json_dict = request.get_json() 
    
    try:
        username = json_dict.get('username',None)
    except KeyError:
        return abort(400)
    
    ##if not username:
    ##    return abort(400)
        
    
    following_user = g.db.users.find_one({'username': username})
    if not following_user:
        return abort(400)
        
    following_userid = ObjectId(following_user['_id'])
    existing_follow = g.db.friendships.find_one({'user_id':user_id, 'following_id':following_userid})
    
    if request.method == 'POST':
        
        g.db.friendships.insert_one({'user_id': user_id, 'following_id': following_userid}) 
        return '', 201 
    
    elif request.method == 'DELETE':
        if existing_follow:
            g.db.friendships.delete_one({'user_id':user_id, 'following_id':following_userid})
            return '', 204
        else:
            return abort(401)
        
@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    
    base_user = g.db.friendships.find({'following_id': ObjectId(user_id)})
    results_list = []
    for user in base_user:
        
        follower = g.db.users.find_one({'_id': ObjectId(user['user_id'])})
        follower_username = follower['username']
        
        results_list.append({'username': follower_username, 'uri': '/profile/{}'.format(follower_username)})
    
 
    return jsonify(results_list), 201
 
    

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    followers = g.db.friendships.find({ "user_id": user_id })
    
    following_ids_list = [ObjectId(f['following_id']) for f in followers]
    
    if len(following_ids_list) == 0:
        return jsonify([]), 200 
 
    tweets = g.db.tweets.find({'user_id': {"$in": following_ids_list}}).sort("created", DESCENDING)
    
    tweets_list = []
    for twt in tweets:
        
#        print '{} {}'.format(twt['content'], twt['_id'])
        
        tweets_list.append(
            {'created': datetime.strftime(twt['created'],'%Y-%m-%dT%H:%M:%S'),
             'id': str(twt['_id']),
             'text': twt['content'],
             'uri': '/tweet/{}'.format(str(twt['_id'])),
             'user_id': str(twt['user_id'])
        })
        
        
    #return jsonify(tweets_list), 200
    return json.dumps(tweets_list).encode('utf8'), 200


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found1(e):
    return '', 401

