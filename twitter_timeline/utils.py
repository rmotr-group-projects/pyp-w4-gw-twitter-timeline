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
        # No Header
        if 'Authorization' not in request.headers:
            abort(401)
        else:
            header_token = request.headers['Authorization']
            # Figure out if token in in mongodb
            auth_doc = g.db.auth.find_one({'access_token':header_token})
            if auth_doc:
                # Need check cases where token is in cases of self
                # user_doc = g.db.users.find_one({'_id':auth_doc['user_id']})
                pass
                # Checks if an argument is passed
                if not args:
                    args = (auth_doc['user_id'],)
                return f(*args, **kwargs)
            else:
                abort(401)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.content_type == JSON_MIME_TYPE:
            return f(*args, **kwargs)
        else:
            abort(400)
    return decorated_function
