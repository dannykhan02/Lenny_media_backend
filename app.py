import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
from config import get_config

config_name = os.getenv('FLASK_ENV', 'development')
config_class = get_config(config_name)
app.config.from_object(config_class)

# Override database URL from .env
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///lenny_media.db")

# Import db from models and initialize it with app
from models import db
db.init_app(app)

# Initialize other extensions
api = Api(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Configure CORS
CORS(app,
     origins=app.config.get('CORS_ORIGINS', ["http://localhost:3000"]),
     supports_credentials=True,
     expose_headers=["Set-Cookie"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])

# Import auth blueprint
from auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# JWT configuration
@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    return jsonify({
        "error": "token_expired",
        "message": "The token has expired. Please log in again."
    }), 401

@jwt.invalid_token_loader
def invalid_token_loader(error):
    return jsonify({
        "error": "invalid_token",
        "message": "Signature verification failed."
    }), 401

@jwt.unauthorized_loader
def missing_token_loader(error):
    return jsonify({
        "error": "authorization_required",
        "message": "Request does not contain a valid token."
    }), 401

# Health check endpoints
@app.route('/')
def index():
    return jsonify({
        "message": "Lenny Media Photography API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/health')
def health():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

# Initialize database
def init_database():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "not_found",
        "message": "The requested resource was not found."
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "internal_server_error",
        "message": "An internal server error occurred."
    }), 500

# Run the application
if __name__ == '__main__':
    print("=" * 60)
    print("📸 LENNY MEDIA PHOTOGRAPHY API")
    print("=" * 60)
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    
    # Initialize database
    init_database()
    
    # Start the server
    port = int(os.getenv('PORT', 5000))
    print(f"\n🚀 Server starting on http://localhost:{port}")
    print("📡 Available endpoints:")
    print(f"   - Home: http://localhost:{port}/")
    print(f"   - Health: http://localhost:{port}/health")
    print(f"   - Auth: http://localhost:{port}/api/auth/*")
    print("=" * 60)
    
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)