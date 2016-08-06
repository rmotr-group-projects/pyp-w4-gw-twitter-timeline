import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, request, Response

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
    if request.method == 'POST':
        post_data = request.json
        #print(data)
        if "username" not in post_data:
            return '', 400
        document_user = g.db.users.find_one({"username": post_data['username']})
        if document_user == None:
            return '', 400
        new_follow_document = {
                                "user_id": user_id,
                                "follows": post_data['username'],
                                "follows_id": document_user["_id"]
                                }
        g.db.friendships.insert_one(new_follow_document)
        return Response(status=201, mimetype='application/json')
    elif request.method == 'DELETE':
        delete_data = request.json
        g.db.friendships.delete_one({"user_id": user_id, "follows": delete_data["username"]})
        return '', 204
    else:
        return '', 404


# Followers view ###############################################################
@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    data = request.json
    current_username = username_via_userid(user_id)
    #current_username = g.db.users.find_one({"_id": user_id})['username']
    
    #print(current_username)
    response_db = g.db.friendships.find({'follows': current_username})
    response_list = []
    if response_db != None:
        for document in response_db:
            #print(document)
            doc_username = username_via_userid(document['user_id'])
            #doc_username = g.db.users.find_one({"_id": document['user_id']})['username']
            response_list.append({
                                  "username": doc_username,
                                  "uri": "/profile/{}".format(doc_username)
                                })
    # else:
    #     print("THATS RIGHT IM INIT")
    #     return '', 400
        
    # print(str([i for i in response_db]))
    # if response_db != None:
    #     response_json = json.dumps(response_db)
    # else:
    #     response_json = json.dumps([])
    response_json = json.dumps(response_list) 
    
    return Response(response_json, status=200, mimetype='application/json')
    

# Timeline view ################################################################
@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # Fetch all the users the current user is following and put their names in a list
    dict_following = g.db.friendships.find({'user_id': user_id})
    list_users_following = [(document["follows"], document["follows_id"]) for document in dict_following]
    #print(str(list_users_following))
    #Fetch all the tweets by the users in the previous list
    #g.db.tweets.find({'user_id': user_id})
    
    list_tweets = []
    for user in list_users_following:
        all_tweets = g.db.tweets.find({'user_id': user[1]}).sort("created", -1)
        #all_tweets_unsorted = g.db.tweets.find({'user_id': user[1]})
        # print(type(all_tweets))
        # print("Sorted")
        # for i in all_tweets:
        #     print(i)
        # print("Not sorted")
        # for j in all_tweets_unsorted:
        #     print(j)
        for tweet in all_tweets:
            tweet_id = str(tweet['_id'])
            #print(type(tweet_id))
            #print(tweet)
            list_tweets.append({
                                'created': python_date_to_json_str(tweet['created']),
                                'id': tweet_id,
                                'text': tweet['content'],
                                'uri': '/tweet/{}'.format(tweet_id),
                                'user_id': str(user[1])
                                })
    all_sorted_list_tweets = sorted(list_tweets,key=lambda lista: lista['created'],reverse=True)
    response_json = json.dumps(all_sorted_list_tweets)
    # print("Sorted")
    # for i in all_tweets:
    #     print(i)
    return Response(response_json, status=200, mimetype='application/json')

'''
GET /timeline
Authorization: <ACCESS_TOKEN> (header)
>>>
[
    {
        'created': '2016-06-11T13:00:10',
        'id': <TWEET_ID>,
        'text': <TWEET_TEXT>,
        'uri': '/tweet/<TWEET_ID>',
        'user_id': <USER_ID>
    },
    ...
]
'''


@app.errorhandler(404)
def not_found_404(e):
    return '', 404


@app.errorhandler(401)
def not_found_401(e):
    return '', 401

@app.errorhandler(400)
def not_found_400(e):    
    return '', 400

def username_via_userid(user_id):
    query_db = g.db.users.find_one({"_id": user_id})
    return query_db['username']