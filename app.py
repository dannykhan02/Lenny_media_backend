from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import get_config

# Import models
from models import db, User, Booking, QuoteRequest, Enrollment, Service, PortfolioItem, Cohort, BusinessInfo, ContactMessage, EmailLog

# Get configuration based on environment
config_name = os.getenv('FLASK_ENV', 'development')
app_config = get_config(config_name)

# Initialize Flask app
app = Flask(__name__)

# Apply configuration
app.config.from_object(app_config)

# Initialize extensions
db.init_app(app)
api = Api(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# CORS setup
CORS(app,
     origins=app_config.CORS_ORIGINS,
     supports_credentials=app_config.CORS_SUPPORTS_CREDENTIALS,
     expose_headers=app_config.CORS_EXPOSE_HEADERS,
     methods=app_config.CORS_METHODS,
     allow_headers=app_config.CORS_ALLOW_HEADERS
)

# # Register JWT blocklist check
# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token = TokenBlocklist.query.filter_by(jti=jti).first()
#     return token is not None

# # Import and register API resources
# from resources import register_media_resources

# # Register API resources
# register_media_resources(api)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=app_config.DEBUG, port=5000)