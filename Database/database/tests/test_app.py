import pytest
from app import app
from utils import generate_jwt

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token():
    # Replace "admin_username" and "admin_role" with actual values for an admin user
    return generate_jwt("admin", 1)  # Assuming 1 is the role for admin


@pytest.fixture
def user_token():
    # Replace "user_username" and "user_role" with actual values for a normal user
    return generate_jwt("johndoe", 0)  # Assuming 0 is the role for a normal user

def test_login(test_client):
    response = test_client.post('/login', json={
        "username": "admin",
        "password": "admin_password"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data


####################### Customers ##########################

def test_register_customer(test_client, admin_token):
    response = test_client.post('/db/customers', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Elm St",
        "gender": "Male",
        "marital_status": "Single",
    })
    assert response.status_code == 201


def test_fetch_customers(test_client, admin_token):
    response = test_client.get('/db/customers', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_fetch_customer(test_client, admin_token):
    response = test_client.get('/db/customers/johndoe', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.get_json()["Username"] == "johndoe"


def test_update_customer(test_client, admin_token):
    response = test_client.put('/db/customers/johndoe', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "address": "456 Maple St"
    })
    assert response.status_code == 200

def test_charge_customer(test_client, admin_token):
    response = test_client.post('/db/customers/johndoe/charge', headers={"Authorization": f"Bearer {admin_token}"}, json={"amount": 100000})
    assert response.status_code == 200

def test_subtract_customer(test_client, admin_token):
    response = test_client.post('/db/customers/johndoe/deduct', headers={"Authorization": f"Bearer {admin_token}"}, json={"amount": 100})
    assert response.status_code == 200

def test_delete_customer(test_client, admin_token):
    response = test_client.delete('/db/customers/johndoe', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


####################### Inventory ##########################

def test_add_inventory_item(test_client, admin_token):
    response = test_client.post('/db/inventory', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Test Product",
        "category": "Electronics",
        "price": 299.99,
        "description": "Test description",
        "stock": 10
    })
    assert response.status_code == 201


def test_fetch_inventory(test_client, admin_token):
    response = test_client.get('/db/inventory', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_update_inventory_item(test_client, admin_token):
    response = test_client.put('/db/inventory/1', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "stock": 20
    })
    assert response.status_code == 200


def test_delete_inventory_item(test_client, admin_token):
    response = test_client.delete('/db/inventory/1', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


####################### Sales ##########################

def test_create_sale(test_client, user_token, admin_token):
    # Recreate the customer to ensure it exists
    test_client.post('/db/customers', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Elm St",
        "gender": "Male",
        "marital_status": "Single",
    })

    test_client.post('/db/customers/johndoe/charge', headers={"Authorization": f"Bearer {admin_token}"}, json={"amount": 100000})
    # Add a product to the inventory
    test_client.post('/db/inventory', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Test Product",
        "category": "Electronics",
        "price": 299.99,
        "description": "Test description",
        "stock": 10
    })

    # Check customer's wallet balance
    response = test_client.get('/db/customers/johndoe', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    customer_data = response.get_json()
    assert customer_data["Wallet"] >= 299.99

    # Create a sale
    response = test_client.post('/db/sales', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 11,
        "quantity": 1
    })
    assert response.status_code == 201


def test_fetch_sales(test_client, admin_token):
    response = test_client.get('/db/sales', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_goods_sales(test_client, user_token):
    response = test_client.get('/db/sales/goods', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_specific_goods_sales(test_client, user_token):
    response = test_client.get('/db/sales/good/2', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200

def test_get_customer_sales(test_client, user_token):
    response = test_client.get('/db/sales/customer/johndoe', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_add_to_wishlist(test_client, user_token):
    response = test_client.post('/db/sales/wishlist/johndoe', headers={"Authorization": f"Bearer {user_token}"}, json={"product_id": 2})
    assert response.status_code == 200

def test_get_wishlist(test_client, user_token):
    response = test_client.get('/db/sales/wishlist/johndoe', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_user_recommendations(test_client, user_token, admin_token):
    # Recreate the customer to ensure it exists
    test_client.post('/db/customers', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Elm St",
        "gender": "Male",
        "marital_status": "Single",
    })

    test_client.post('/db/customers/johndoe/charge', headers={"Authorization": f"Bearer {admin_token}"}, json={"amount": 100000})

    # Add related products to the inventory
    products = [
        {"name": "Product A", "category": "Electronics", "price": 100.00, "description": "Description A", "stock": 10},
        {"name": "Product B", "category": "Electronics", "price": 150.00, "description": "Description B", "stock": 10},
        {"name": "Product C", "category": "Electronics", "price": 200.00, "description": "Description C", "stock": 10}
    ]
    for product in products:
        test_client.post('/db/inventory', headers={"Authorization": f"Bearer {admin_token}"}, json=product)

    # Create sales for related products
    for i in range(1, 4):
        test_client.post('/db/sales', headers={"Authorization": f"Bearer {user_token}"}, json={
            "product_id": i,
            "quantity": 1
        })

    # Get recommendations
    response = test_client.get('db/sales/recommendations/johndoe', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


####################### Reviews ##########################

def test_submit_review(test_client, user_token):
    response = test_client.post('/reviews', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 2,
        "rating": 5,
        "comment": "Great product!"
    })
    assert response.status_code == 201

def test_update_review(test_client, user_token):
    # Create a review first
    response = test_client.post('/reviews', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 2,
        "rating": 5,
        "comment": "Temporary review for update test"
    })
    assert response.status_code == 201

    # Fetch the review to get its ID
    response = test_client.get('/reviews/product/2', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    reviews = response.get_json()
    assert len(reviews) > 0

    # Use the ID of the most recent review
    review_id = reviews[-1]["ReviewID"]

    # Update the review
    response = test_client.put(f'/reviews/{review_id}', headers={"Authorization": f"Bearer {user_token}"}, json={
        "rating": 4,
        "comment": "Good product!"
    })
    assert response.status_code == 200

def test_fetch_reviews(test_client, admin_token, user_token):
    # Create a review first
    response = test_client.post('/reviews', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 2,
        "rating": 5,
        "comment": "Temporary review for fetch test"
    })
    assert response.status_code == 201

    # Fetch the review to get its ID
    response = test_client.get('/reviews/product/2', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    reviews = response.get_json()
    assert len(reviews) > 0

    # Use the ID of the most recent review
    review_id = reviews[-1]["ReviewID"]

    # Fetch the specific review by ID
    response = test_client.get(f'/reviews/{review_id}', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200

def test_fetch_product_reviews(test_client, user_token):
    response = test_client.get('/reviews/product/2', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_fetch_customer_reviews(test_client, user_token):
    response = test_client.get('/reviews/customer/johndoe', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_moderate_review(test_client, admin_token):
    response = test_client.put('/reviews/1/moderate', headers={"Authorization": f"Bearer {admin_token}"}, json={
        "status": "Approved"
    })
    assert response.status_code == 200


def test_delete_review(test_client, admin_token, user_token):
    # Create a review
    response = test_client.post('/reviews', headers={"Authorization": f"Bearer {user_token}"}, json={
        "product_id": 2,
        "rating": 5,
        "comment": "Temporary review for deletion test"
    })
    assert response.status_code == 201

    # Fetch the review to get its ID
    response = test_client.get('/reviews/product/2', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    reviews = response.get_json()
    assert len(reviews) > 0

    # Use the ID of the most recent review (assumption: the review we just created is the last one)
    review_id = reviews[-1]["ReviewID"]

    # Delete the review
    response = test_client.delete(f'/reviews/{review_id}', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.get_json() == {"message": "Review deleted successfully."}
