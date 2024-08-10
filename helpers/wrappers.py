from functools import wraps
from flask import request, jsonify
import json
import os
import json
import json
import os

class Wrappers:
    @staticmethod
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'X-API-KEY' not in request.headers:
                return jsonify({"error": "Authorization header missing"}), 401
            
            # Retrieve the API key from the request header
            api_key = request.headers.get('X-API-KEY')
            # Check if the API key is valid
            if api_key and api_key == os.getenv('X-API-KEY'):
                return f(*args, **kwargs)
            else:
                # If the API key is incorrect or not provided, return 401 unauthorized error
                return jsonify({"error": "API key is invalid or missing"}), 401
        return decorated_function