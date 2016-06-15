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
        token = request.headers.get('Authorization')
        cursor = g.db.auth.find_one({'access_token': token})
        if cursor is None:
            abort(401)
        # cram in userid to decorated function    
        return f(cursor['user_id'] , *args, **kwargs)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.json is None: #Verify Json in, else abort & throw 400
            abort(400)
        return f(*args, **kwargs)
    return decorated_function
