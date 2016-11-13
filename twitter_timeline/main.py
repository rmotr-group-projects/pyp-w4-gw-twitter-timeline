import json

from pymongo import MongoClient
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
    json_data = request.get_json()
    if not json_data.get('username', None):
        abort(400)
    username = json_data['username']
    user_followed = g.db.users.find_one({'username': username})
    if not user_followed:
        abort(400)
    else:
        user_followed_id = user_followed['_id']
    followed = g.db.friendships.find_one({'user': ObjectId(user_id), 'followed': user_followed_id})

    if request.method == 'POST':
        if not followed:
            g.db.friendships.insert_one({'user': ObjectId(user_id), 'followed': user_followed_id})
            return '', 201
    
    if request.method == 'DELETE':
        
        # https://docs.mongodb.com/v3.2/reference/method/db.collection.deleteOne/#db.collection.deleteOne
        # result = g.db.friendships.deleteOne({}) # include our filtration criteria here
        # find the friendship, check it exists
        # return '', 400 # if it doesn't exist
        # delete the friendship
        g.db.friendships.delete_many({'user': user_id, 'followed': user_followed})
        return '', 204 
    


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    # friendship {follower_id: user_id, followed_username: request.data['username']}
    # when you get followers, it should be a list with dictionaries containing the friendship
    # [{'username': 'testuser1', 'uri': '/profile/testuser1'}]
    # import ipdb; ipdb.set_trace()
    # print(user_id)
    # user = g.db.users.find({'user_id': user_id})
    # print(user)
    # https://docs.mongodb.com/v3.2/reference/method/db.collection.find/
    # g.db.friendships.insert_one({'user': user_id, 'followed': user_followed_id})
    follower_list = g.db.friendships.find({ 'followed': ObjectId(user_id) }) #  # get a list of the ppl following the user
    # print(follower_list)
    response = []

    # should work once we get friendships    
    for follower in follower_list:
        import ipdb; ipdb.set_trace()
        response.append({
            'username': 'something',
            'uri': '/profile/{}'.format('something')
        })
        
    return jsonify(response)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # user_ids_followed = g.db.friendships.find({ follower_id: user_id })
    # friendship {follower_id: user_id, followed_username: request.data['username']}
    # tweets = g.db.tweets({}) 
    # get the tweets of all the people the user is following 
    # (no need to get user's own tweets unlike actual twitter)
    # sort tweets by latest first https://docs.mongodb.com/v3.2/reference/method/cursor.sort/

    response = []
    
    # should work once we figure the rest out
    # for tweet in tweets:
    #     response.append({
    #         'created': python_date_to_json_string(tweet['created']),
    #         'id': str(tweet['_id'],
    #         'text': tweet['content'],
    #         'uri': '/tweet/{}'.format('TBD'),
    #         'user_id': str(tweet['user_id')
    #     })
    return jsonify(response)
    