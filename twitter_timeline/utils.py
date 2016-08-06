import hashlib
import string
import random
from datetime import datetime
from functools import wraps

from flask import request, g, abort

JSON_MIME_TYPE = 'application/json'


def md5(token):
    new_token = token
    if str != bytes:
        new_token = token.encode('utf-8')
    return hashlib.md5(new_token)


def generate_random_token(size=15):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def sqlite_date_to_python(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def python_date_to_json_str(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def auth_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #print(request.headers)
        # Checks to see if 'Authorization' was even put into the request header
        if 'Authorization' not in request.headers:
            abort(401)
        else:
            auth_doc_current_user = g.db.auth.find_one({"access_token": request.headers['Authorization']})
            if auth_doc_current_user == None:
                abort(401)
            user_id = auth_doc_current_user['user_id']
        # print("AUTH:" + auth_doc_current_user['Authorization'])
        # print(auth_doc_current_user)
        # if auth_doc_current_user['Authorization'] == None:
        #     abort(401)
        
        # Get the user_id from the user collection and store it in a kwarg
        # if g.db.auth.find_one() == None:
        #print(request.headers['Authorization'])
        #print(auth_doc_current_user)
        # for this in user_id:
        #     print(this)
            
        # print("THIS IS ME" + str(user_id))
        # print("[]"*10)
        #print(user_id)
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type != JSON_MIME_TYPE:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function
