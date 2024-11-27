import sqlite3
from flask import current_app
def get_db_connection():
    """
    Get a connection to the database.
    Uses the database path from Flask's app config.
    """
    db_path = current_app.config.get('DATABASE', 'ecommerce.db')  # Default to 'ecommerce.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn