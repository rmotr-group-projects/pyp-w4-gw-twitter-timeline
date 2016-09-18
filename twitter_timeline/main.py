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
def friendship():
    data = request.get_json()
    if 'username' not in data:
        return '', 400
    valid_usernames_cur = g.db.users.find({},{'_id':0,'username':1})
    if {'username': data['username']} not in list(valid_usernames_cur):
        return '', 400
    follower = _access_token_to_username(request.headers['Authorization'])
    data['follower'] = follower
    if request.method == 'POST':
        g.db.friendships.insert(data)
        return '', 201
    else:
        g.db.friendships.remove(data)
        return '', 204


@app.route('/followers', methods=['GET'])
@auth_only
def followers():
    username = _access_token_to_username(request.headers['Authorization'])
    followers_cur = g.db.friendships.find({'username':username},{'_id':0,'follower':1})
    followers_list =[]
    for row in followers_cur:
        uname = row['follower']
        followers_list.append({'username': uname, 'uri': '/profile/{}'.format(uname)})
    return json.dumps(followers_list)
    
def _access_token_to_username(access_token):
    userid_cur = g.db.auth.find({'access_token':access_token},{'_id':0,'user_id':1}).limit(1)
    userid = list(userid_cur)[0]['user_id']
    username_cur = g.db.users.find({'_id':userid},{'_id':0, 'username':1})
    username = list(username_cur)[0]['username']
    return username

def _username_to_user_id(username):
    userid_cur = g.db.users.find({'username':username},{'_id':1})
    userid = list(userid_cur)[0]['_id']
    return userid

@app.route('/timeline', methods=['GET'])
@auth_only
def timeline():
    username = _access_token_to_username(request.headers['Authorization'])
    following_cur = g.db.friendships.find({'follower':username},{'_id':0,'username':1})
    following = list(following_cur)
    if following == []:
        return json.dumps([])
    all_tweets =[]
    for x in following:
        uid = _username_to_user_id(x['username'])
        u_tweets_cur = g.db.tweets.find({'user_id':uid})
        for tweet in u_tweets_cur:
            newtweet ={}
            newtweet['created'] = python_date_to_json_str(tweet['created'])
            newtweet['id'] = str(tweet['_id'])
            newtweet['text'] = tweet['content']
            newtweet['uri'] = '/tweet/{}'.format(tweet['_id'])
            newtweet['user_id'] = str(tweet['user_id'])
            all_tweets.append(newtweet)
    sorted_tweets = sorted(all_tweets, key=lambda k: k['created'], reverse=True)
    return json.dumps(sorted_tweets)
    
@app.errorhandler(404)
def not_found(e):
    return '', 404


@app.errorhandler(401)
def not_found(e):
    return '', 401
