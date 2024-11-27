import random

def generate_unique_username(base="user"):
    """Generate a unique username for tests."""
    return f"{base}_{random.randint(1000, 9999)}"

def test_create_customer(client):
    unique_username = generate_unique_username("janedoe")
    data = {
        "full_name": "Jane Doe",
        "username": unique_username,
        "password": "password123",
        "age": 28,
        "address": "456 Maple St",
        "gender": "Female",
        "marital_status": "Married"
    }
    response = client.post('/db/customers', json=data)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Customer registered successfully"

def test_fetch_customer(client):
    unique_username = generate_unique_username("johndoe")
    test_create_customer(client)
    response = client.get(f'/db/customers/{unique_username}')
    assert response.status_code == 200
    assert response.get_json()["FullName"] == "Jane Doe"

def test_delete_customer(client):
    unique_username = generate_unique_username("johndoe")
    test_create_customer(client)
    response = client.delete(f'/db/customers/{unique_username}')
    assert response.status_code == 200
    assert response.get_json()["message"] == "Customer deleted successfully"