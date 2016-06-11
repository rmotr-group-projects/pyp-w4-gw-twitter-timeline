# -*- coding: utf-8 -*-
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
        new_token = str(token).encode('utf-8')
    return hashlib.md5(new_token)


def generate_random_token(size=15):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def sqlite_date_to_python(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def python_date_to_json_str(dt):
    # return dt.strftime("%Y-%m-%dT%H:%M:%S")
    return dt.isoformat()


def auth_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        # Extract auth token from headers
        token = request.headers.get('Authorization')
        
        # Find record that matches that token
        auth_record = g.db.auth.find_one({'access_token': token})
        
        if not auth_record:
            abort(401)
        
        # Get the user_id for the user who matches that token
        user_id = auth_record['user_id']
        
        # Append the user_id to the list of arguments passed to the decorated
        #  function when it is called.
        #   User calls
        #       f(args)
        #   And function definition is written as
        #       def f(user_id, args):
        new_args = (user_id,) + args
        
        return f(*new_args, **kwargs)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        # Verify that json is supplied in the request
        if request.json is None:
            abort(400)
        
        return f(*args, **kwargs)
    return decorated_function
