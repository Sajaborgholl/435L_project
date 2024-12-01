import pytest
from unittest.mock import MagicMock, patch
from inventory.app.app import app
from inventory.app.utils import generate_jwt

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
    return "Bearer " + generate_jwt("johndoe", 0)  # Assuming role `0` is for regular user


# Tests for inventory routes

def test_fetch_inventory(test_client, user_token, mocker):
    """Test retrieving all inventory items."""
    mock_get = mocker.patch("inventory.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"item_id": 1, "name": "Item A", "stock": 10},
        {"item_id": 2, "name": "Item B", "stock": 5}
    ])

    response = test_client.get(
        '/inventory', headers={"Authorization": user_token})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_item(test_client, admin_token, mocker):
    """Test creating a new inventory item."""
    mock_post = mocker.patch("inventory.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {
        "message": "Item created successfully"
    })

    response = test_client.post('/inventory', headers={"Authorization": admin_token}, json={
        "name": "New Item",
        "category": "Electronics",
        "price": 99.99,
        "description": "A new electronic item",
        "stock": 50
    })
    assert response.status_code == 201
    assert "message" in response.get_json()


def test_modify_item(test_client, admin_token, mocker):
    """Test modifying an existing inventory item."""
    mock_put = mocker.patch("inventory.app.app.requests.put")
    mock_put.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Item updated successfully"
    })

    response = test_client.put(
        '/inventory/1', headers={"Authorization": admin_token}, json={
            "price": 89.99,
            "stock": 45
        })
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_deduct_stock_from_item(test_client, admin_token, mocker):
    """Test deducting stock from an inventory item."""
    mock_post = mocker.patch("inventory.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Stock deducted successfully"
    })

    response = test_client.post(
        '/inventory/1/deduct', headers={"Authorization": admin_token}, json={
            "count": 5
        })
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_remove_item(test_client, admin_token, mocker):
    """Test deleting an inventory item."""
    mock_delete = mocker.patch("inventory.app.app.requests.delete")
    mock_delete.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Item deleted successfully"
    })

    response = test_client.delete(
        '/inventory/1', headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert "message" in response.get_json()
