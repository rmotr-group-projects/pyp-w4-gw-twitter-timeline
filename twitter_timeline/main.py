import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, Response, abort

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
def add_friendship():
    user_id = get_user_id(request)
    username = get_username(user_id)

    # must catch valid json, but missing username.
    if 'username' in request.json:
        user_to_follow = request.json['username']
    else:
        user_to_follow = None
    user_to_follow_db = g.db.users.find_one({'username': user_to_follow})

    if not all((user_to_follow, user_to_follow_db)): 
        abort(400)
    
    # lookup target user
    user_to_follow_id = user_to_follow_db['_id']
    user_to_follow_username = user_to_follow_db['username']


    if user_id == user_to_follow_id:
        abort(401)
    
    # already following
    if g.db.friendships.find({'follower_id':user_id,'followed_id':user_to_follow_id}).count() > 0:
        abort(404)
        
    new_entry = { 
        'follower_id': user_id,  # this is the huge entire table of that user.
        'follower_name': username,
        'followed_id': user_to_follow_id,
        'followed_name': user_to_follow_username
    }
                
    g.db.friendships.insert_one(new_entry)
    return Response('', 201)
    

@app.route('/friendship', methods=['DELETE'])
@json_only
@auth_only
def delete_friendship():
    user_id = get_user_id(request)
    username = get_username(user_id)

    # must catch valid json, but missing username.
    if 'username' in request.json:
        user_to_follow = request.json['username']
    else:
        user_to_follow = None
    user_to_follow_db = g.db.users.find_one({'username': user_to_follow})

    if not all((user_to_follow, user_to_follow_db)): 
        abort(400)
    
    # lookup target user 
    user_to_follow_id = user_to_follow_db['_id']

    if user_id == user_to_follow_id:
        abort(401)

    # make sure entry exists
    if g.db.friendships.find({'follower_id':user_id,'followed_id':user_to_follow_id}).count() == 0:
        abort(404)
    
    # Should try and catch an exception if the database fails to delete this properly.
    g.db.friendships.delete_many({'follower_id': user_id, 'followed_id': user_to_follow_id})
    
    return Response('',204)
    

@app.route('/followers', methods=['GET'])
@auth_only
def followers():
    user_id = get_user_id(request)

    followed_db = g.db.friendships.find({'followed_id':user_id})

    followers = []
    for user in followed_db:
        username = user['follower_name']
        new = {
            'username': username,
            'uri': '/profile/{}'.format(username)
        }
        followers.append(new)
        
    return Response(json.dumps(followers), 200, content_type=JSON_MIME_TYPE) 


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline():
    # get this user.  575b5c2bab63bca09af707a5
    user_id = get_user_id(request)

    followed_db = g.db.friendships.find({'follower_id': user_id})

    followed_ids = [entry['followed_id'] for entry in followed_db]

    # iterate over that followed IDs, slurping in tweets, to make a timeline.
    all_tweets = []
    for followed_id in followed_ids:
        tweet_cursor = g.db.tweets.find({'user_id': followed_id})
        for tweet in tweet_cursor:
            # borrowed this code section, mine was not working well.
            new_tweet = dict(created=python_date_to_json_str(tweet['created']), 
                            id = str(tweet['_id']),
                            text=tweet['content'], 
                            uri='/tweet/{}'.format(str(tweet['_id'])),
                            user_id=str(followed_id))
            all_tweets.append(new_tweet)
            
    sorted_tweets = sorted(all_tweets, key=lambda k: k['created'], reverse=True)
    
    return Response(json.dumps(sorted_tweets), 200, content_type=JSON_MIME_TYPE) 
    

@auth_only
def get_user_id(request):
    authkey = request.headers.get('Authorization')
    db_authkey = g.db.auth.find_one({'access_token': authkey})
    return db_authkey['user_id']


def get_username(user_id):
    return g.db.users.find_one({'_id': user_id})['username']
    
    
@app.errorhandler(404)
def not_found(e):
    return Response('', 404)


@app.errorhandler(401)
def not_found(e):
    return Response('', 401)
