import os, json, secrets
from datetime import datetime
from flask import Blueprint, request, jsonify

bp_keys = Blueprint('keys', __name__)
KEY_FILE = os.path.join(os.getcwd(), 'api_keys.json')

def load_keys():
    if not os.path.exists(KEY_FILE):
        return {}
    with open(KEY_FILE, 'r') as f:
        return json.load(f)
    
def save_keys(data):
    with open(KEY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@bp_keys.route('/api/register', methods=['POST'])
def register_key():
    """
    프론트엔드에서 '제출' 요청시, 새로운 api_key를 생성해서 제공
    """
    user = request.json.get('username')
    if not user:
        return jsonify({'error': 'Need username'}), 400
    
    new_key = secrets.token_urlsafe(32)

    data = load_keys()
    data[new_key] = {
        'owner': user,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    save_keys(data)

    return jsonify({'api_keys': new_key}), 201

from functools import wraps

def valid_key(key):
    data = load_keys()
    return key in data

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-KEY')
        if not key or not valid_key(key):
            return jsonify({'error': 'No Key available.'}), 401
        return f(*args, **kwargs)
    return decorated
