import pytest
import os
import sys
import sqlite3

# Add the `database` directory to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from initialize_db import initialize_db
from connect_db import get_db_connection
from app import app

TEST_DB = "test_ecommerce.db"

@pytest.fixture(scope="module")
def test_app():
    """
    Create a test app with the application context.
    """
    app.config["TESTING"] = True
    app.config["DATABASE"] = TEST_DB

    with app.app_context():
        # Initialize the test database
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        initialize_db(TEST_DB)
        yield app

        # Clean up the test database after tests
        try:
            # Explicitly close any lingering connections
            sqlite3.connect(TEST_DB).close()
        except sqlite3.Error as e:
            print(f"Error closing lingering connection: {e}")

        if os.path.exists(TEST_DB):
            try:
                os.remove(TEST_DB)
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
