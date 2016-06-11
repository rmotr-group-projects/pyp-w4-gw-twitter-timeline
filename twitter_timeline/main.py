# -*- coding: utf-8 -*-
import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import abort, Flask, g, request, Response

from twitter_timeline import settings
from twitter_timeline.utils import *

app = Flask(__name__)

JSON_MIME_TYPE = 'application/json'


# Helper functions go here:
def connect_db(db_name):
    mongo = MongoClient(settings.FULL_MONGO_HOST)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


# Views go here:
@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):
    '''
    Creates or deletes a "following relationship" between an authenticated
    user and another user whose username is sent in a POST json object.
    '''
    
    # Verify a username was sent
    try:
        followed_username = request.json['username']
    except:
        abort(400)
    
    # Verify that user exists
    followed_user = g.db.users.find_one({'username': followed_username})
    if not followed_user:
        abort(400)
    
    # Get the follower object from the users collection
    follower = g.db.users.find_one({'_id': ObjectId(user_id)})
    
    # You can't follow yourself.  That's just silly.
    if followed_user['_id'] == follower['_id']:
        abort(400)
    
    # Get the list of users already being followed.  This should be initialized
    #  as a blank list if the 'following' key does not exist.
    follower.setdefault('following', [])
    following = follower['following']
    # # One-liner for above
    # following = follower['following'] if 'following' in follower else []
    
    if request.method == 'POST':
        # Append the followed user's id to the follower list if it is not 
        #  already in it.  If already following, return a Bad Request response.
        if followed_user['_id'] not in following:
            following.append(followed_user['_id'])
            response = Response(status=201, mimetype=JSON_MIME_TYPE)
        else:
            abort(400)
    
    elif request.method == 'DELETE':
        # Remove the followed user's id from the follower list if it is already
        #  in it.  If not already following, return a Bad Request response.
        if followed_user['_id'] in following:
            following.remove(followed_user['_id'])
            response = Response(status=204, mimetype=JSON_MIME_TYPE)
        else:
            abort(400)
        
    # Update the users collection with the new or revised following list
    g.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'following': following}}
    )
    
    # If we successfully reach this point, return the appropriate response
    return response


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    '''
    Returns list of users following the authenticated user.
    '''
    # The list of users to be returned
    followers = []
    
    # Get all users who have the authenticated user in their 'following' list
    for follower in g.db.users.find({ 'following': {'$in': [user_id]}}):
        
        # Format the required follower details properly
        user_name = follower['username']
        follower_details = {
            "username": user_name,
            "uri": "/profile/{}".format(user_name)
        }
        
        # Append this follower to the list
        followers.append(follower_details)

    # Return the follower list in a Success response
    response = Response(
        json.dumps(followers),
        status=200
    )
    
    return response


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    '''
    Timeline section to return JSON of tweet details made by users the
    authenticated user is following.
    '''
    
    # The list of tweets to be returned
    tweets = []
    
    # Get the authenticated user
    user = g.db.users.find_one({'_id': user_id})
    
    # Populate timeline if the authenticated user is following any other users
    if 'following' in user:
    
        # Get tweets from every followed user to add the tweet list
        for following_id in user['following']:
            
            # Get at all this user's tweets and append them to the list
            for tweet in g.db.tweets.find({'user_id': following_id}):
                
                # Format the required tweet details properly
                tweet_details = {
                    'created': tweet['created'].isoformat(),
                    'id': str(tweet['_id']),
                    'text': tweet['content'],
                    'uri': '/tweet/{}'.format(tweet['_id']),
                    # 'uri': '/tweet/' + str(tweet['_id']),
                    'user_id': str(tweet['user_id'])
                }
                
                # Append this tweet to the list
                tweets.append(tweet_details)
    
        # Sort the tweets by date created, from newest to oldest
        tweets = sorted(tweets, key=lambda k: k['created'], reverse=True)
    
    # Return the tweet list in a success response
    response = Response(
        json.dumps(tweets),
        status=200
    )
    
    return response


# Error handlers go here:
@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
