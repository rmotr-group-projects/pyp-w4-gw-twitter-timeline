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
    request_user = convert_token_to_id(request.headers.get('Authorization'))#######
    g.db.followers.insert({'user_id':request_user, 'follows':leader_username})
    g.db.commit()
    return '', 201


@app.route('/followers', methods=['GET'])
@auth_only
def followers():
    pass


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

#helper functions
def convert_token_to_id(token):
    print('enter')
    cur = g.db.find({'access_token':token})
    return list(cur)['user_id']
