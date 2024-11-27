def test_create_customer(client):
    data = {
        "full_name": "Grace Hopper",
        "username": "graceh",
        "password": "password123",
        "age": 85,
        "address": "1024 Loop St",
        "gender": "Female",
        "marital_status": "Single"
    }
    response = client.post('/db/customers', json=data)
    assert response.status_code == 201
    assert response.get_json().get("message") == "Customer registered successfully"


def test_fetch_customer(client):
    # Create a customer first
    test_create_customer(client)
    response = client.get('/db/customers/graceh')
    assert response.status_code == 200
    customer = response.get_json()
    assert customer.get("Username") == "graceh"
    assert customer.get("FullName") == "Grace Hopper"


def test_fetch_all_customers(client):
    # Fetch all customers
    response = client.get('/db/customers')
    assert response.status_code == 200
    customers = response.get_json()
    assert isinstance(customers, list)
    # Should have at least one customer (admin user), plus any others we've added
    assert len(customers) >= 1
    usernames = [customer["Username"] for customer in customers]
    assert "admin" in usernames
    # Create a new customer and check again
    test_create_customer(client)
    response = client.get('/db/customers')
    customers = response.get_json()
    assert len(customers) >= 2
    usernames = [customer["Username"] for customer in customers]
    assert "graceh" in usernames


def test_modify_customer(client):
    # Create a customer
    test_create_customer(client)

    # Update customer data
    update_data = {
        "full_name": "Grace Murray Hopper",
        "age": 86,
        "address": "2048 Nested Loop St"
    }
    response = client.put('/db/customers/graceh', json=update_data)
    assert response.status_code == 200
    assert response.get_json().get("message") == "Customer updated successfully"

    # Verify updates
    response = client.get('/db/customers/graceh')
    customer = response.get_json()
    assert customer.get("FullName") == "Grace Murray Hopper"
    assert customer.get("Age") == 86
    assert customer.get("Address") == "2048 Nested Loop St"


def test_delete_customer(client):
    # Create a customer
    test_create_customer(client)
    response = client.delete('/db/customers/graceh')
    assert response.status_code == 200
    assert response.get_json().get("message") == "Customer deleted successfully"

    # Verify deletion
    response = client.get('/db/customers/graceh')
    assert response.status_code == 404
    assert response.get_json().get("error") == "Customer not found"


def test_add_money_to_wallet(client):
    # Create a customer
    test_create_customer(client)

    # Add funds
    add_funds = {"amount": 150.0}
    response = client.post('/db/customers/graceh/charge', json=add_funds)
    assert response.status_code == 200
    assert response.get_json().get("message") == "Customer account charged successfully"

    # Verify wallet balance
    response = client.get('/db/customers/graceh')
    customer = response.get_json()
    assert customer.get("Wallet") == 150.0


def test_subtract_money_from_wallet(client):
    # Create a customer and add funds
    test_create_customer(client)
    client.post('/db/customers/graceh/charge', json={"amount": 150.0})

    # Deduct funds
    deduct_funds = {"amount": 100.0}
    response = client.post('/db/customers/graceh/deduct', json=deduct_funds)
    assert response.status_code == 200
    assert response.get_json().get("message") == "Money deducted from wallet successfully"

    # Verify wallet balance
    response = client.get('/db/customers/graceh')
    customer = response.get_json()
    assert customer.get("Wallet") == 50.0


def test_subtract_money_insufficient_funds(client):
    # Create a customer without adding funds
    test_create_customer(client)

    # Attempt to deduct funds
    deduct_funds = {"amount": 50.0}
    response = client.post('/db/customers/graceh/deduct', json=deduct_funds)
    assert response.status_code == 400
    assert response.get_json().get("error") == "Insufficient funds"