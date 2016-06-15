import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, request

from twitter_timeline import settings
from twitter_timeline.utils import *

import settings

app = Flask(__name__)

JSON_MIME_TYPE = 'application/json'


def connect_db(db_name = settings.DATABASE_NAME):
    mongo = MongoClient(settings.FULL_MONGO_HOST)
    return mongo[db_name]


@app.before_request
def before_request():
    g.db = connect_db(settings.DATABASE_NAME)


@app.route('/friendship', methods=['POST', 'DELETE'])
@json_only
@auth_only
def friendship(user_id):
    if not "username" in request.data.json(): return abort(400)
    #get target user, verify if exists
    target_user = g.db.user.find({"username": username})
    if target_user: #If it exists, get a list of followers
        target_user = target_user[0]
        followers = g.db.friendship.find({"user_id":target_user})
        if followers:
            followers = followers[0]
        
    #if post, follow
    if request.method == 'POST':
        #include ourselves inside target follower list
        if user_id not in followers:
                followers.append(user_)

    #if delete, unfollow
    elif request.method == 'DELETE':
        meow = g.db.
        '''
        {
            "helen_id":["somenotveryniceguy", "someotherguy"].
            "rose_id":[],
            "luis_id":[],
            "obama_id":[]
        }
        '''
        
        pass
            "elen
    pass


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    #Check if the header includes Auth_token
    #Query token in auth collection(table), to obtain the user
    if "Authorization" in request.headers:
        cursor = g.db.auth.find({"access_token": request.headers['Authorization']})
        user_id = cursor[0]["user_id"]
        
        users = g.db.user.find({"user_id": user_id})
        followers = user[0]["followers"]
        return json.dumps(followers)

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    pass


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
