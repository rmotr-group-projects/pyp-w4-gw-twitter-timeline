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
users collection has:
_id, username, password, first_name, last_name, birth_date
and two optional parameters: [followers], [following]

tweets collection has:
_id, user_id, content, created

auth collections has:
user_id, access_token

'''

def _update_db(d, field, action, value, db):
    '''
    If action is 'append' it will either make a new list for d[field] = [value] or 
    append value to an existing list
    If action is 'remove' it will remove value from the list
    After it will update the db with $set
    '''
    if action == 'append' and field not in d:
        d[field] = [value]
    else:
        
        getattr(d[field], action)(value)
        
    result= g.db.users.update_one(
        {'_id': d['_id']},
        {
            "$set": {field: d[field]}
        })
    return result # returns UpdateResult object
    
@app.route('/reset_friendships') # just for testing purposes
@auth_only
def reset_friendships(user_id):
    g.db.users.update_many(
        {},
        {
            "$set": {
                'following': [],
                'followers': []
            }
        })
    return Response("Friendships reset", 200)
    
@app.route('/show_friendships') # just for testing purposes
@auth_only
def show_friendships(user_id):
    all_users = g.db.users.find({})
    for user in all_users:
        print(user['username'])
        print('Following: '),
        for person in user.get('following',[]):
            print(person[1]),
        print('\nFollowers: '),
        for person in user.get('followers',[]):
            print(person[1]),
        print('\n' + '-'*10)
    return Response('Printed to terminal', 200)
    
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
    user_username = user_data['username']
    
    if user_id == friend_id:
        return Response('{} cannot follow themself'.format(friend_username), 401)
    
    if request.method == 'POST':
        # check if connection already exists
        if [friend_id, friend_username] in user_data.get('following', []):
            msg = '{} is already following {}'.format(user_username, friend_username)
            return Response(msg, 404)
            
        result1 = _update_db(user_data, 'following', 'append', [friend_id, friend_username], g.db)
        result2 = _update_db(friend_data, 'followers', 'append', [user_id, user_username], g.db)

        msg = "Created\n{} is now following {}".format(user_username, friend_username)
        return Response(msg, 201)
        
    elif request.method == 'DELETE':
        # make sure entry exists
        if [friend_id, friend_username] not in user_data.get('following', []):
            msg = '{} is not following {} so nothing to delete'.format(user_username, friend_username)
            return Response(msg, 404)
        elif [user_id, user_username] not in friend_data.get('followers', []):
            msg = '{} is not followed by {} which should not happen!'.format(friend_username, user_username)
            return Response(msg, 404)
        
        result1 = _update_db(user_data, 'following', 'remove', [friend_id, friend_username], g.db)
        result2 = _update_db(friend_data, 'followers', 'remove', [user_id, user_username], g.db)
            
        return Response('',204)

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    entries = g.db.users.find_one({'_id': user_id}).get('followers',[])
    followers = [dict(username=entry[1], uri='/profile/{}'.format(entry[1])) for entry in entries]

    return Response(json.dumps(followers), 200, content_type=JSON_MIME_TYPE) 

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # returns list of all tweets who you are following
        
    people = g.db.users.find_one({'_id':user_id}).get('following',[]) # [(id, name), (id, name)...]
    
    all_tweets = []
    for person in people:
        tweet_cursor = g.db.tweets.find({'user_id': person[0]})
        for tweet in tweet_cursor:
            
            new_tweet = dict(created=python_date_to_json_str(tweet['created']), 
                            id = str(tweet['_id']),
                            text=tweet['content'], 
                            uri='/tweet/{}'.format(str(tweet['_id'])),
                            user_id=str(person[0]))
            all_tweets.append(new_tweet)
            
    # sort by creation date
    sorted_tweets = sorted(all_tweets, key=lambda x: x['created'], reverse=True)
    
    return Response(json.dumps(sorted_tweets), 200, content_type=JSON_MIME_TYPE) 

@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
