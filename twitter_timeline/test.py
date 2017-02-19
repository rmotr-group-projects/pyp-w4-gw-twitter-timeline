from pymongo import MongoClient
from bson.objectid import ObjectId

from twitter_timeline import settings
from twitter_timeline import app
from twitter_timeline.utils import md5

from datetime import datetime, timedelta

app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'testing secret key'

mongo = MongoClient(settings.FULL_MONGO_HOST)
db = mongo[settings.DATABASE_NAME]

client = app.test_client()

"""
for col_name in ['users', 'tweets', 'auth', 'friendships']:
    db[col_name].drop()

users = [
            {
                '_id': ObjectId('575b5c2bab63bca09af707a5'),
                'username': 'testuser1',
                'password': md5('user1-pass').hexdigest(),
                'first_name': 'Test',
                'last_name': 'User',
                'birth_date': '2016-01-30'
            },
            {
                '_id': ObjectId('575b5c2bab63bca09af707a4'),
                'username': 'testuser2',
                'password': md5('1234').hexdigest(),
            },
            {
                '_id': ObjectId('575b5c2bab63bca09af707a3'),
                'username': 'testuser3',
                'password': md5('1234').hexdigest(),
            },
        ]

res = db.users.insert(users)
user_1_id = res[0]
user_2_id = res[1]
user_3_id = res[2]

tweets = [
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c883'),
                'user_id': user_1_id,
                'content': 'Tweet 1 testuser1',
                'created': datetime(2016, 6, 11, 12, 0, 0),
            },
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c884'),
                'user_id': user_1_id,
                'content': 'Tweet 2 testuser1',
                'created': datetime(2016, 6, 11, 12, 0, 5),
            },
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c885'),
                'user_id': user_2_id,
                'content': 'Tweet 1 testuser2',
                'created': datetime(2016, 6, 11, 13, 0, 0),
            },
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c886'),
                'user_id': user_2_id,
                'content': 'Tweet 2 testuser2',
                'created': datetime(2016, 6, 11, 13, 0, 5),
            },
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c887'),
                'user_id': user_2_id,
                'content': 'Tweet 3 testuser2',
                'created': datetime(2016, 6, 11, 13, 0, 10),
            },
            {
                '_id': ObjectId('575b5d00ab63bca12dc5c888'),
                'user_id': user_3_id,
                'content': 'Tweet 1 testuser3',
                'created': datetime(2016, 6, 11, 13, 0, 7),
            }
        ]
db.tweets.insert(tweets)


user_1_access_token = "$RMOTR$-U1"
user_2_access_token = "$RMOTR$-U2"
user_3_access_token = "$RMOTR$-U3"

access_tokens = [
    {
        'user_id': user_1_id,
        "access_token": user_1_access_token
    },
    {
        'user_id': user_2_id,
        "access_token": user_2_access_token
    },
    {
        'user_id': user_3_id,
        "access_token": user_3_access_token
    }
]
db.auth.insert(access_tokens)
"""

query = db.users.find()
print(query)
#query2 = db.auth.find({})
for x in query:
    print(x['username'], x['_id'])
    q = db.auth.find_one({'user_id': x['_id']})

    print("Q=",q['access_token'])