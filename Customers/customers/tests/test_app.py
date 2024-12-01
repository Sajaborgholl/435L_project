import pytest
from unittest.mock import MagicMock, patch
from customers.app.app import app
from customers.app.utils import generate_jwt

# Fixtures for test client and tokens


@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token():
    """Generate a mock JWT token for an admin."""
    return "Bearer " + generate_jwt("admin", 1)  # Assuming role `1` is for admin


@pytest.fixture
def user_token():
    """Generate a mock JWT token for a regular user."""
    return "Bearer " + generate_jwt("johndoe", 0)  # Assuming role `0` is for a regular user


# Test cases for customers routes

def test_register_customer(test_client, user_token, mocker):
    """Test customer registration."""
    mock_post = mocker.patch("customers.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {
        "message": "Customer registered successfully"
    })

    response = test_client.post('/customers/register', headers={"Authorization": user_token}, json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_delete_customer(test_client, admin_token, mocker):
    """Test deleting a customer."""
    mock_delete = mocker.patch("customers.app.app.requests.delete")
    mock_delete.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Customer deleted successfully"
    })

    response = test_client.delete(
        '/customers/johndoe', headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_update_customer(test_client, admin_token, mocker):
    """Test updating a customer's information."""
    mock_put = mocker.patch("customers.app.app.requests.put")
    mock_put.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Customer updated successfully"
    })

    response = test_client.put('/customers/johndoe', headers={"Authorization": admin_token}, json={
        "address": "456 New St",
        "age": 31
    })
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_get_customer(test_client, user_token, mocker):
    """Test retrieving a specific customer's information."""
    mock_get = mocker.patch("customers.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "username": "johndoe",
        "full_name": "John Doe",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })

    response = test_client.get(
        '/customers/johndoe', headers={"Authorization": user_token})
    assert response.status_code == 200
    assert "username" in response.get_json()


def test_get_all_customers(test_client, admin_token, mocker):
    """Test retrieving all customers."""
    mock_get = mocker.patch("customers.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"username": "johndoe", "full_name": "John Doe"},
        {"username": "janedoe", "full_name": "Jane Doe"}
    ])

    response = test_client.get(
        '/customers', headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_charge_wallet(test_client, user_token, mocker):
    """Test adding money to a customer's wallet."""
    mock_post = mocker.patch("customers.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Wallet charged successfully"
    })

    response = test_client.post('/customers/johndoe/charge', headers={"Authorization": user_token}, json={
        "amount": 100.0
    })
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_deduct_wallet(test_client, user_token, mocker):
    """Test deducting money from a customer's wallet."""
    mock_post = mocker.patch("customers.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Wallet deducted successfully"
    })

    response = test_client.post('/customers/johndoe/deduct', headers={"Authorization": user_token}, json={
        "amount": 50.0
    })
    assert response.status_code == 200
    assert "message" in response.get_json()
