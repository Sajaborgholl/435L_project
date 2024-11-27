import os
import sys
import pytest
from database.initialize_db import initialize_db

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'  # In-memory DB
    initialize_db()  # Pass the schema path to the initialize_db function
    client = app.test_client()
    yield client

