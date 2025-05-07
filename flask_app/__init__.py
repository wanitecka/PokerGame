from flask import Flask
from flask_app.routes import register_routes, os

def create_app():
    os.makedirs('data', exist_ok=True)
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY='your_secret_key',
        DATABASE='path_to_your_database'
    )

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app