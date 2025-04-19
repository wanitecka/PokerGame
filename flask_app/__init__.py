from flask import Flask
from flask_app.routes import register_routes

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY='your_secret_key',
        DATABASE='path_to_your_database'
    )

    # Register routes
    register_routes(app)

    return app