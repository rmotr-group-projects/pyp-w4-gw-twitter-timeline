import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import (Flask, g, abort, Response)

from twitter_timeline import settings
from twitter_timeline.utils import *
import pymongo

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
    if 'username' not in request.json:
        abort(400)
    leader_username = request.json.get('username')
    usernames = g.db.users.find({'username':leader_username})
    if not list(usernames):
        abort(400)
    if request.method == 'POST':
        request_user = convert_token_to_id(request.headers.get('Authorization'))
        g.db.followers.insert({'follower_id':request_user, 'leader_username':leader_username})
        return '', 201
    if request.method == 'DELETE':
        request_user = convert_token_to_id(request.headers.get('Authorization'))
        g.db.followers.remove({'leader_username':leader_username})
        return '', 204


@app.route('/followers', methods=['GET'])
@auth_only
def followers():
    req_user_id = convert_token_to_id(request.headers.get('Authorization'))
    req_user_username = convert_id_to_username(req_user_id)
    cur = g.db.followers.find({'leader_username':req_user_username})
    arr = []
    for item in cur:
        username = convert_id_to_username(item['follower_id'])
        my_dict = {
            'username':username,
            'uri':'/profile/%s'%username
        }
        arr.append(my_dict)
    return json.dumps(arr)


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline():
    user_id = convert_token_to_id(request.headers.get('Authorization'))
    cur = g.db.followers.find({'follower_id':user_id})#all that the user follows
    arr_of_leaders = []
    for x in cur:
        arr_of_leaders.append(x['leader_username'])
    arr_of_leaders = map(convert_username_to_id, arr_of_leaders)
    arr_of_tweets = []
    for leader in arr_of_leaders:
        curs = g.db.tweets.find({'user_id':leader})
        for item in curs:
            arr_of_tweets.append(item)
    arr_of_results = []
    for xy in arr_of_tweets:
        id = str(xy['_id'])
        text = xy['content']
        twitter_user_id = str(xy['user_id'])
        created = str(xy['created'])
        my_dict = { 'created':created, 'id':id, 'text':text, 'uri':'/tweet/%s'%id, 'user_id':twitter_user_id }
        arr_of_results.append(my_dict)
    arr_of_results.sort(key=lambda item: item['created'], reverse=True)
    return json.dumps(arr_of_results)


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401


#helper functions
def convert_token_to_id(token):#works now!
    cur = g.db.auth.find_one({'access_token':token})
    return cur['user_id']


def convert_id_to_username(id):#works also!
    id = ObjectId(id)
    cur = g.db.users.find_one({'_id':id})
    return cur['username']


def convert_username_to_id(username):
    cur = g.db.users.find_one({'username':username})
    return ObjectId(cur['_id'])




