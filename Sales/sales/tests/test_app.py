import pytest
from sales.app.app import app
from sales.app.utils import generate_jwt
from unittest.mock import MagicMock, patch


# Fixtures for test client and tokens
@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token():
    """Generate a JWT token for an admin."""
    return generate_jwt("admin", 1)  # Assuming role `1` is for admin


@pytest.fixture
def user_token():
    """Generate a JWT token for a regular user."""
    return generate_jwt("johndoe", 0)  # Assuming role `0` is for a regular user


@pytest.fixture(autouse=True)
def mock_jwt_required():
    """Mock the `jwt_required` decorator globally."""
    with patch("sales.app.utils.jwt_required", lambda: lambda x: x):
        yield


# Sales Tests
def test_create_sale(test_client, user_token, mocker):
    """Test creating a new sale record."""
    mock_post = mocker.patch("sales.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {
        "message": "Sale recorded successfully",
        "sale_id": 12345
    })

    response = test_client.post('/sales', headers={"Authorization": f"Bearer {user_token}"}, json={
        "customer_username": "johndoe",
        "product_id": 1,
        "quantity": 2
    })
    assert response.status_code == 201


def test_get_sales(test_client, user_token, mocker):
    """Test retrieving all sales records."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"sale_id": 1, "product_id": 1, "quantity": 2},
        {"sale_id": 2, "product_id": 2, "quantity": 1}
    ])

    response = test_client.get(
        '/sales', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_goods_sales(test_client, user_token, mocker):
    """Test retrieving available goods for sale."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"product_id": 1, "name": "Product A"},
        {"product_id": 2, "name": "Product B"}
    ])

    response = test_client.get(
        '/sales/goods', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_specific_good(test_client, user_token, mocker):
    """Test retrieving details of a specific good."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "product_id": 1,
        "name": "Product A",
        "details": "Detailed description of the product."
    })

    response = test_client.get(
        '/sales/good/1', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert "name" in response.get_json()


def test_get_purchases(test_client, user_token, mocker):
    """Test retrieving a customer's purchase history."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"sale_id": 1, "product_id": 1, "quantity": 2},
        {"sale_id": 2, "product_id": 2, "quantity": 1}
    ])

    response = test_client.get(
        '/sales/customer/johndoe', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_add_to_user_wishlist(test_client, user_token, mocker):
    """Test adding a product to a customer's wishlist."""
    mock_post = mocker.patch("sales.app.app.requests.post")
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Product added to wishlist"
    })

    response = test_client.post('/sales/wishlist/johndoe', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 1
    })
    assert response.status_code == 200


def test_get_user_wishlist(test_client, user_token, mocker):
    """Test retrieving a customer's wishlist."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"product_id": 1, "name": "Product A"},
        {"product_id": 2, "name": "Product B"}
    ])

    response = test_client.get(
        '/sales/wishlist/johndoe', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_recommendations(test_client, user_token, mocker):
    """Test fetching recommendations for a customer."""
    mock_get = mocker.patch("sales.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"product_id": 3, "name": "Recommended Product A"},
        {"product_id": 4, "name": "Recommended Product B"}
    ])

    response = test_client.get(
        '/sales/recommendations/johndoe', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
