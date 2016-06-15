import json
import pdb
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, jsonify

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
def friendship():
    
    friend_name = field_in_request("username")
    
    my_name = get_username_from_id(get_id_from_token())
    
    friend_dict = {"username": my_name ,"uri": "/profile/" + my_name}  
    
    if request.method == "POST":
        
        if not update_users("username", friend_name, "$push", "friends", friend_dict):
        
            # No user with friend_name in db
            abort(400)
            
        update_users("username", my_name, "$push", "following", get_id_from_username(friend_name))

        return("", 201)
    
    elif request.method == "DELETE":
        update_users("username", friend_name, "$pull", "friends", friend_dict)
        
        return("", 204)


def update_users(field, field_value, method, lst_name, lst_value):
    return g.db.users.update_one(
            { field: field_value },
                { 
                    method: { lst_name: lst_value } 
                }
        )
    
def get_id_from_token():
    return g.db.auth.find_one({"access_token": request.headers['Authorization']})["user_id"]
    
    
def get_username_from_id(user_id):
    return g.db.users.find_one({"_id": user_id})["username"]
    
    
def get_id_from_username(username):
    try:
        return g.db.users.find_one({"username": username})["_id"]
    except TypeError:
        abort(400)

def field_in_request(field_name):
    if field_name not in request.json:
        abort(400)
        
    return request.json[field_name]

@app.route('/followers', methods=['GET'])
@auth_only
def followers():
    
    return jsonify(g.db.users.find_one({"_id": get_id_from_token()})["friends"])
    



@app.route('/timeline', methods=['GET'])
@auth_only
def timeline():
    tweets = []
    user_id = get_id_from_token()
    following = g.db.users.find_one({"_id": user_id})["following"]
    
    cursor = g.db.tweets.find( {"user_id": { "$in": following }} )
    sorted_cursor = cursor.sort("created",pymongo.DESCENDING)
    
    for el in sorted_cursor:
        tweet_dict = {
            'created': python_date_to_json_str(el['created']),
            'id': str(el["_id"]),
            'text': el['content'],
            'uri': '/tweet/' + str(el["_id"]),
            'user_id': str(el["user_id"])
        }
        tweets.append(tweet_dict)
    
    return jsonify(tweets)

    
    


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
