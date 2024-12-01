import pytest
from reviews.app.app import app
from reviews.app.utils import generate_jwt
from unittest.mock import MagicMock

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


####################### Reviews Tests ##########################

def test_create_review(test_client, user_token, mocker):
    """Test submitting a review."""
    # Mock external POST request
    mock_post = mocker.patch("requests.post")
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {
        "message": "Review created successfully"
    })

    response = test_client.post('/reviews', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 1,
        "rating": 5,
        "comment": "Great product!"
    })
    assert response.status_code == 201


def test_fetch_product_reviews(test_client, user_token, mocker):
    """Test fetching reviews for a product."""
    # Mock the external GET request
    mock_get = mocker.patch("reviews.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"review_id": 1, "rating": 5, "comment": "Excellent!"},
        {"review_id": 2, "rating": 4, "comment": "Good value for money"}
    ])

    response = test_client.get(
        '/reviews/product/1', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_fetch_customer_reviews(test_client, user_token, mocker):
    """Test fetching reviews by a specific customer."""
    # Mock the external GET request
    mock_get = mocker.patch("reviews.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: [
        {"review_id": 1, "rating": 5, "comment": "Great product!"},
        {"review_id": 2, "rating": 4, "comment": "Good product!"}
    ])

    response = test_client.get(
        '/reviews/customer/johndoe', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_modify_review(test_client, user_token, mocker):
    """Test modifying an existing review."""
    # Mock the external PUT request
    mock_put = mocker.patch("reviews.app.app.requests.put")
    mock_put.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Review updated successfully"
    })

    response = test_client.put(
        '/reviews/1',
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "rating": 4,
            "comment": "Updated review"
        }
    )
    assert response.status_code == 200


def test_remove_review(test_client, user_token, mocker):
    """Test deleting a review."""
    # Mock the external DELETE request
    mock_delete = mocker.patch("reviews.app.app.requests.delete")
    mock_delete.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Review deleted successfully"
    })

    response = test_client.delete(
        '/reviews/1', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


def test_fetch_review_details(test_client, user_token, mocker):
    """Test fetching details of a specific review."""
    # Mock the external GET request
    mock_get = mocker.patch("reviews.app.app.requests.get")
    mock_get.return_value = MagicMock(status_code=200, json=lambda: {
        "review_id": 1,
        "product_id": 1,
        "rating": 5,
        "comment": "Fantastic product!"
    })

    response = test_client.get(
        '/reviews/1', headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert "rating" in response.get_json()


def test_moderate_review(test_client, admin_token, mocker):
    """Test moderating a review (admin only)."""
    # Mock the external PUT request
    mock_put = mocker.patch("reviews.app.app.requests.put")
    mock_put.return_value = MagicMock(status_code=200, json=lambda: {
        "message": "Review moderated successfully"
    })

    response = test_client.put(
        '/reviews/1/moderate',
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "Approved"}
    )
    assert response.status_code == 200
