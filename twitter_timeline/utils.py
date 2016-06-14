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
        # http://stackoverflow.com/questions/29386995/how-to-get-http-headers-in-flask
        authkey = request.headers.get('Authorization')
        
        db_auth = g.db.auth.find_one({'access_token': authkey})
        db_authkey = db_auth['access_token'] if db_auth else None
        
        #db_authkey = g.db.auth.find_one({'access_token': authkey})['access_token']
        if not all((authkey, db_authkey, authkey == db_authkey)):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def json_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # exact same as twitter API!
        if request.get_json() is None:
            abort(400)
        return f(*args, **kwargs)
    return decorated_function
