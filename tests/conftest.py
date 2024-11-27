import os
import tempfile
import pytest
from database.app import app
from database.initialize_db import initialize_db

@pytest.fixture
def client():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    app.config['TESTING'] = True
    app.config['DATABASE'] = temp_db_path  # Set the test database path

    with app.app_context():
        initialize_db(temp_db_path)

    yield app.test_client()

    os.close(temp_db_fd)
    os.remove(temp_db_path)