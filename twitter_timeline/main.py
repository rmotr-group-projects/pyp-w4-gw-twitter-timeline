import json

from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, g, Response, request

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


@app.route('/friendship', methods=['POST', 'DELETE', 'GET'])
@json_only
@auth_only
def friendship(user_id):
    # Check if there's a valid (JSON) request, and what user that request is asking to friend
    request_json = request.get_json()
    if 'username' in request_json:
        request_username = request_json['username']
        try:
            request_user_id = get_user_id_from_name(request_username)
        except:
            abort(400)
    else:
        abort(400)
    
    '''friendship should look like {{_id:id, following:[user_id_objects], followers:[user_id_objects] user_id:user_id_object}}'''

    friendship_collection = g.db.friendships
    user_friendship_doc = friendship_collection.find_one({'user_id':user_id})

    # Create new friendship
    if request.method == 'POST':
        # If user ID is already being followed Conflict is given
        if request_user_id in user_friendship_doc['following']:
            return Response(status=409)
        else:
            # If bad username request
            if not get_username_from_id(request_user_id):
                return Response(status=400)

            # Updates the user to follow the requested user
            friendship_collection.update(
            {
                'user_id':user_id}, 
            {
                '$push':
                {'following':request_user_id}
            })
            
            # Updates the requested user (by the)
            g.db.friendships.update(
            {
                'user_id':request_user_id},
            {
                '$push':
                {'followers':user_id}
            })
                
            return Response(status=201)                

    # Remove friendship
    elif request.method == 'DELETE':
        if request_user_id in user_friendship_doc['following']:

            # Updates the user to follow the requested user
            friendship_collection.update(
            {
                'user_id':user_id}, 
            {
                '$pull':
                {'following':request_user_id}
            })

            # Updates the requested user (by the)
            g.db.friendships.update(
            {
                'user_id':request_user_id},
            {
                '$pull':
                {'followers':user_id}
            })
            
            return Response(status=204)
        else:
            return Response(status=400)
    # Unsupported request method
    else:
        abort(400)


@app.route('/followers', methods=['GET'])
@auth_only
def followers(user_id):
    # Get followers of user, returns a JSON
    if request.method == 'GET':
        friendship_collection = g.db.friendships
        user_friendship_doc = friendship_collection.find_one({'user_id':user_id})
        if 'followers' in user_friendship_doc:
            followers_list = [
                get_username_from_id(follower_id)
                for follower_id in user_friendship_doc['followers']
            ]
            response_list = [
                {'username':follower, 'uri':'/profile/{}'.format(follower)}
                for follower in followers_list
            ]
            response_json = json.dumps(response_list)
            return Response(response_json, status=201, mimetype='application/json')
        
        # Returns empty list because forever alone
        else:
            response_json = json.dumps([])
            return Response(response_json, status=201, mimetype='application/json')

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

# Gets the user name from id
def get_username_from_id(user_id):
    user_doc = g.db.users.find_one({'_id':user_id})
    if user_doc:
        return user_doc['username']
    else:
        return None

# Gets user id from username
def get_user_id_from_name(username):
    user_doc = g.db.users.find_one({'username':username})
    if user_doc:
        return user_doc['_id']
    else:
        return None
    

    
    