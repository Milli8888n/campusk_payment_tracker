import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.customer import customer_bp
from src.routes.room import room_bp
from src.routes.contracts import contract_bp
from werkzeug.exceptions import RequestEntityTooLarge
import time
from collections import defaultdict, deque

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Performance configurations
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_timeout': 20,
    'pool_recycle': -1,
    'pool_pre_ping': True
}

# Simple rate limiting
rate_limit_storage = defaultdict(lambda: deque())
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

def rate_limit():
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    now = time.time()
    
    # Clean old requests
    while rate_limit_storage[client_ip] and rate_limit_storage[client_ip][0] < now - RATE_LIMIT_WINDOW:
        rate_limit_storage[client_ip].popleft()
    
    # Check rate limit
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': f'Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds'
        }), 429
    
    # Add current request
    rate_limit_storage[client_ip].append(now)
    return None

@app.before_request
def before_request():
    # Apply rate limiting to API routes only
    if request.path.startswith('/api/'):
        rate_limit_response = rate_limit()
        if rate_limit_response:
            return rate_limit_response

# Enable CORS for all routes
CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'])

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(room_bp, url_prefix='/api')
app.register_blueprint(contract_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import all models to ensure they are registered
from src.models.customer import Customer, Contract, WebBooking, Alert
from src.models.room import Branch, Room, RoomBooking, RoomAlert, WebRoomBooking

db.init_app(app)
with app.app_context():
    db.create_all()

# Error handlers
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    }), 413

@app.errorhandler(429)
def handle_rate_limit(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests, please try again later'
    }), 429

@app.errorhandler(500)
def handle_internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end'
    }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
