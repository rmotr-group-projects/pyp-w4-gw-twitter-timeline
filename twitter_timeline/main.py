import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, request, Response, abort

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


# Friendship view ##############################################################
@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):
    # The content of the POST or DELETE will be returned in a dictionary.
    data = request.json
    if request.method == 'POST':
        # Checks to see if any username was sent via POST. Otherwise 400 error.
        if "username" not in data:
            abort(400)
        # Fetch only the info for user sent via POST from the users collection.
        # Also fetch the current user using the user id from the access token.
        current_user = username_via_userid(user_id)
        document_user = g.db.users.find_one({"username": data['username']})
        # Checks to see if username sent via POST exists. Otherwise 400 error.
        if document_user == None:
            abort(400)
        # Create the follow document for the two users and fill it with relevant data.
        new_follow_document = {
                                "user": current_user,
                                "user_id": user_id,
                                "follows": data['username'],
                                "follows_id": document_user["_id"]
                                }
        # Insert the follow document inside the friendships collection.                         
        g.db.friendships.insert_one(new_follow_document)
        return Response(status=201, mimetype='application/json')
    elif request.method == 'DELETE':
        # Delete the follow document of the two users.
        g.db.friendships.delete_one({"user_id": user_id, "follows": data["username"]})
        return Response(status=204)
    # GET (or any other method) is not allowed on this view.
    else:
        abort(404)


# Followers view ###############################################################
@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    data = request.json
    # Fetch all the documents for users following the current user.
    response_db = g.db.friendships.find({'follows_id': user_id})
    response_list = []
    # Returns an empty list if no one follows the user.
    if response_db != None:
        # Populate the list with users that follows the current user.
        for document in response_db:
            response_list.append({
                                  "username": document["user"],
                                  "uri": "/profile/{}".format(document["user"])
                                })
    response_json = json.dumps(response_list) 
    
    return Response(response_json, status=200, mimetype='application/json')
    

# Timeline view ################################################################
@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # Fetch all the users the current user is following and put their names in a list.
    dict_following = g.db.friendships.find({'user_id': user_id})
    list_users_following = [(document["follows"], document["follows_id"]) for document in dict_following]
    list_tweets = []
    for user in list_users_following:
        all_tweets = g.db.tweets.find({'user_id': user[1]}) #.sort("created", -1)
        for tweet in all_tweets:
            tweet_id = str(tweet['_id'])
            list_tweets.append({
                                'created': python_date_to_json_str(tweet['created']),
                                'id': tweet_id,
                                'text': tweet['content'],
                                'uri': '/tweet/{}'.format(tweet_id),
                                'user_id': str(user[1])
                                })
    all_sorted_list_tweets = sorted(list_tweets,key=lambda lista: lista['created'],reverse=True)
    response_json = json.dumps(all_sorted_list_tweets)
    return Response(response_json, status=200, mimetype='application/json')
    
def username_via_userid(user_id):
    query_db = g.db.users.find_one({"_id": user_id})
    return query_db['username']