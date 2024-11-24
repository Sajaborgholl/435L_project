from flask import Flask
from .controllers import register_routes


def create_app():
    app = Flask(__name__)

    # Configure the app (e.g., database path, secret keys, etc.)
    app.config['DB_PATH'] = '../../database/ecommerce.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Register routes
    register_routes(app)

    return app
