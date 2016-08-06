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
    # Create new friendship
    if request.method == 'POST':
        pass
    # Remove friendship
    elif request.method == 'DELETE':
        pass
    # Unsupported request method
    else:
        abort(400)


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    # Get followers of user
    if request.method == 'GET':
        pass
    # Unsupported request method
    else:
        abort(400)
        


@app.route('/timeline', methods=['GET'])
@auth_only
def timeline(user_id):
    # Get timeline of user
    if request.method == 'GET':
        pass
    # Unsupported request method
    else:
        abort(400)


@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
