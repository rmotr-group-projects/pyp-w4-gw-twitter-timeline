import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, url_for, Response

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

'''
http://twitter-timeline-davidgranas.c9users.io:8080/friendship
body:
{
    "username" : "testuser2"
}
header:
Authorization   $RMOTR$-U1

users collection has:
_id, username, password, first_name, last_name, birth_date

tweets collection has:
_id, user_id, content, created

auth collections has:
user_id, access_token

friendships collection: follower -> followed
follower_id, follower_username, followed_id, followed_username
'''

@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):

    data = request.get_json()
    if 'username' not in data:
        return Response('Username field missing', 400)
        
    friend_username = data['username']
    friend_data = g.db.users.find_one({'username': friend_username})
    
    if not friend_data:
        return Response('No user found with username {}'.format(friend_username), 400)
    
    friend_id = friend_data['_id']
    user_data = g.db.users.find_one({'_id': user_id})
    
    if user_id == friend_id:
        return Response('{} cannot follow themself'.format(friend_username), 401)
    
    if request.method == 'POST':
        if g.db.friendships.find({'follower_id':user_id,'followed_id':friend_id}).count() > 0:
            msg = '{} is already following {}'.format(user_data['username'], friend_username)
            return Response(msg, 404)
            
        # add the logged in user to the friendships collection of the POST user
        new_entry = dict(follower_id = user_id,
                        follower_name = user_data['username'],
                        followed_id = friend_id,
                        followed_name = friend_username
                    )
                    
        g.db.friendships.insert_one(new_entry)
        msg = "Created\n{} is now following {}".format(user_data['username'], friend_username)
        return Response(msg, 201)
        
    elif request.method == 'DELETE':
        # make sure entry exists
        if g.db.friendships.find({'follower_id':user_id,'followed_id':friend_id}).count() == 0:
            msg = '{} is not following {} so nothing to delete'.format(user_data['username'], friend_username)
            return Response(msg, 404)
        
        g.db.friendships.delete_many({'follower_id': user_id, 
            'followed_id': friend_data['_id']
        })
        # 204 can't include a message body...
        return Response('',204)

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    # followed will be from the header used_id
    followed_cursor = g.db.friendships.find({'followed_id':user_id})
    # get the followers of the followed
    followers = [dict(username=entry['follower_name'], 
                uri='/profile/{}'.format(entry['follower_name']))
                for entry in followed_cursor]

    return Response(json.dumps(followers), 200, content_type=JSON_MIME_TYPE) 

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # returns list of all tweets of the followed
        
    follower_cursor = g.db.friendships.find({'follower_id':user_id})
    
    # get the ids of all the followed
    followed_ids = [entry['followed_id'] for entry in follower_cursor]
    
    all_tweets = []
    for followed_id in followed_ids:
        tweet_cursor = g.db.tweets.find({'user_id': followed_id})
        for tweet in tweet_cursor:
            
            new_tweet = dict(created=python_date_to_json_str(tweet['created']), 
                            id = str(tweet['_id']),
                            text=tweet['content'], 
                            uri='/tweet/{}'.format(str(tweet['_id'])),
                            user_id=str(followed_id))
            all_tweets.append(new_tweet)
            
    # need to sort by creation date
    # newlist = sorted(list_to_be_sorted, key=lambda k: k['name']) 
    sorted_tweets = sorted(all_tweets, key=lambda k: k['created'], reverse=True)
    
    return Response(json.dumps(sorted_tweets), 200, content_type=JSON_MIME_TYPE) 

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
