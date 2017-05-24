import json

from pymongo import MongoClient
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
    """
    two alternatives:
    {'follower': followers_user_id, 'followed': followee_user_id}
    this is traditional database model--let's not do this^^
    
    second option:
    {'followers_id': followers_id, 'followed_people':[username1, username2, ...]}
    
    cursor = db.restaurants.find({"borough": "Manhattan"})
    """
    if request.method == 'POST':
        followed_person_username = request.get_json().get('username')
        record = g.db.users.find_one({'username': followed_person_username})
        if record is None:
            return '', 400
        
        record = g.db.friendships.find_one({'followers_id':user_id})
        if record is None:
            g.db.friendships.insert({'followers_id': user_id, 'followed_people': [followed_person_username]})
            return '', 201
        elif followed_person_username not in record['followed_people']:
            record['followed_people'].append(followed_person_username)
            g.db.friendships.find_one_and_update({'followers_id': user_id}, {'$set': {'followed_people': record['followed_people']}})
            return '', 201
            
    if request.method == 'DELETE':
        person_to_unfollow = request.get_json().get('username')
        record = g.db.friendships.find_one({'followers_id':user_id})
        if record is None:
            return '', 400
            
        if person_to_unfollow in record['followed_people']:
            record['followed_people'].remove(person_to_unfollow)
        
        g.db.friendships.find_one_and_update({'followers_id': user_id}, {'$set': {'followed_people': record['followed_people']}})
        return '', 204

def get_user_name(user_id):
    user = g.db.users.find_one({'_id': ObjectId(user_id)})
    username = user['username']
    return username
    
def get_user_id(username):
    user = g.db.users.find_one({'username': username})
    user_id = user['_id']
    return user_id

@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    """
    want all the followers of the user with user_id
    {'username': 'testuser1', 'uri': '/profile/testuser1'},
    {'username': 'testuser3', 'uri': '/profile/testuser3'}
    
    all_friendships = [
    {'followers_id': 1, 'followed_people': ['bob', 'diane']},
    {'followers_id': 2, 'followed_people': ['bob', 'marc']},
    {'followers_id': 3, 'followed_people': ['marc']}]
    """
    """
    {'_id': ObjectId(123)}
    g.db.users.find_one({'_id': "123"))
    """
    username = get_user_name(user_id)
    all_friendships = g.db.friendships.find()
    followers_names = []
    for record in all_friendships:
        if username in record['followed_people']:
            followers_names.append(get_user_name(record['followers_id']))
    followers_dict_list = [{'username': name, 'uri': '/profile/{}'.format(name)} for name in followers_names]
    return json.dumps(followers_dict_list), 201

    
@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    """
    get the people that user_id follows from the friendships table
    for each person in that list,
        get all their tweets and add to some tweet list
    sort the tweets
    return the list of tweets wrapped in a dictionary
    g.db.tweets.find({'user_id': 5}) is [{}, {}, {}]
    
    dictionary for tweets we want:
    {
        'created': '2016-06-11T13:00:00',
        'id': '575b5d00ab63bca12dc5c885',
        'text': 'Tweet 1 testuser2',
        'uri': '/tweet/575b5d00ab63bca12dc5c885',
        'user_id': '575b5c2bab63bca09af707a4'
    }
    
    what we have:
    {
        '_id': ObjectId('575b5d00ab63bca12dc5c888'),
        'user_id': self.user_3_id,
        'content': 'Tweet 1 testuser3',
        'created': datetime(2016, 6, 11, 13, 0, 7),
    }
    
    >>> d = {'_id':5}                                                                                                                                               
    >>> d['id'] = d.pop('_id')                                                                                                                                      
    >>> d                                                                                                                                                           
    {'id': 5}
    
    >>> str(d)                                                                                                                                                     
    '2009-01-04 01:02:03'
    
    """
    tweets_to_show = []
    record = g.db.friendships.find_one({'followers_id':user_id})
    if record is None:
        return json.dumps([]), 200
    #import pdb
    #pdb.set_trace()
    for person in record['followed_people']:
        person_id = get_user_id(person)
        
        tweets_to_show.extend(g.db.tweets.find({'user_id': ObjectId(person_id)}))
    #tweets_to_show.extend(g.db.tweets.find({'user_id': ObjectId(user_id)}))
    
    tweets_to_show.sort(key=lambda tweet: tweet['created'], reverse=True)
    
    # now repackage our tweets
    for tweet in tweets_to_show:
        date_string = str(tweet['created'])
        tweet['created'] = "T".join(date_string.split())
        tweet['id'] = str(tweet.pop('_id'))
        tweet['text'] = tweet.pop('content')
        tweet['uri'] = '/tweet/' + str(tweet['id'])
        tweet['user_id'] = str(tweet['user_id'])
        
        

    return json.dumps(tweets_to_show), 200


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
