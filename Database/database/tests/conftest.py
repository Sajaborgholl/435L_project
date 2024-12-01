import pytest
import os
import sys
import sqlite3
import tempfile
import time

# Add the `database` directory to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from initialize_db import initialize_db
from connect_db import get_db_connection
from app import app

@pytest.fixture(scope="module")
def test_app():
    """
    Create a test app with the application context.
    """
    app.config["TESTING"] = True
    
    # Create a unique temporary database file for each test run
    test_db = tempfile.mktemp(suffix=".db")
    app.config["DATABASE"] = test_db

    with app.app_context():
        # Initialize the test database
        if os.path.exists(test_db):
            os.remove(test_db)
        initialize_db(test_db)
        
        # Enable WAL mode for better concurrency
        enable_wal_mode(test_db)
        
        yield app
        
        # Clean up the test database after tests
        try:
            # Explicitly close any lingering connections
            conn = sqlite3.connect(test_db)
            conn.close()
        except sqlite3.Error as e:
            print(f"Error closing lingering connection: {e}")

        # Give it a moment to release the file handle
        time.sleep(1)

        # Remove the temporary database file
        if os.path.exists(test_db):
            try:
                os.remove(test_db)
            except PermissionError as e:
                print(f"Error deleting test database: {e}")


@pytest.fixture
def test_client(test_app):
    """
    Provide a test client for sending requests to the app.
    """
    return test_app.test_client()


@pytest.fixture
def db_connection(test_app):
    """
    Provide a database connection within the app context.
    """
    with test_app.app_context():
        conn = get_db_connection()
        yield conn
        conn.close()


def enable_wal_mode(db_name):
    """
    Enable Write-Ahead Logging mode for better concurrency in SQLite.
    """
    conn = sqlite3.connect(db_name)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    conn.close()
