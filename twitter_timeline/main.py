# -*- coding: utf-8 -*-
import json

from pymongo import MongoClient, DESCENDING
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
    
    if request.method == 'DELETE':
        # Remove the followed user's id from the follower list if it is already
        #  in it.  If not already following, return a Bad Request response.
        if followed_user['_id'] in following:
            following.remove(followed_user['_id'])
            response = Response(status=204, mimetype=JSON_MIME_TYPE)
        else:
            abort(400)
        
    # Update the users collection with the new or revised following list
    result = g.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$set': {'following': following}
        }
    )
    
    # If we successfully reach this point, return the appropriate response
    return response


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    '''
    Followers section to return JSON of users following the authenticated user.
    '''
    # This represents the json object we will return
    followers = []
   
    # Query for passed user_id in the users collection.
    for follower in g.db.users.find({ 'following': {'$in' : [ user_id ]}}):
        
        # Assign result to username and setup dictionary to be appended
        user_name = follower['username']
        follower_details = {
            "username": str(user_name),
            "uri": "/profile/" + str(user_name)
        }
        
        # Append results to followers list for later return
        followers.append(follower_details)


    # If we successfully reach this point, return the appropriate response
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
    
    # This represents the json object we will return
    tweet_list = []
    tweets = []
    
    # Get user's following list
    user = g.db.users.find_one({'_id': user_id})
    
    # Populate timeline if user is following any other users
    if 'following' in user:
    
        # Query for only 'following' field from the user_id passed from the users collection
        for following_id in user['following']:
            
            # Obtain tweet details from the results
            for tweet in g.db.tweets.find({'user_id': following_id}):
                
                # Assign results to variables and setup dictionary to be appended
                tweet_details = {
                    'created': tweet['created'].isoformat(),
                    'id': str(tweet['_id']),
                    'text': tweet['content'],
                    'uri': '/tweet/' + str(tweet['_id']),
                    'user_id': str(tweet['user_id'])
                }
                
                # Append dictionary to running tweet_list for later sorting
                tweet_list.append(tweet_details)
    
        # Sort list of dictionary elements by date value
        tweets = sorted(tweet_list, key=lambda k: k['created'], reverse=True)
    
    # If we successfully reach this point, return the appropriate response
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
