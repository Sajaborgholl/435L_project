import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crud_customers import (
    register_customer,
    delete_customer,
    update_customer,
    get_all_customers,
    get_customer_by_username,
    charge_customer,
    deduct_money
)

def test_register_customer(test_app):
    # Valid customer registration
    response = register_customer(
        full_name="John Doe",
        username="johndoe",
        password="securepassword",
        age=30,
        address="123 Elm St",
        gender="Male",
        marital_status="Single"
    )
    assert response == {"message": "Customer registered successfully"}
    
    # Attempt to register with an existing username
    response = register_customer(
        full_name="Jane Doe",
        username="johndoe",  # Same username as before
        password="anotherpassword",
        age=25,
        address="456 Oak St",
        gender="Female",
        marital_status="Married"
    )
    assert response == {"error": "Username already taken"}


def test_get_customer_by_username(test_app):
    # Existing customer
    customer = get_customer_by_username("johndoe")
    assert customer is not None
    assert customer["Username"] == "johndoe"
    assert customer["FullName"] == "John Doe"

    # Non-existing customer
    customer = get_customer_by_username("nonexistent")
    assert customer is None


def test_update_customer(test_app):
    # Update an existing customer
    response = update_customer("johndoe", full_name="Johnathan Doe", age=35)
    assert response == {"message": "Customer updated successfully"}

    # Verify update
    customer = get_customer_by_username("johndoe")
    assert customer["FullName"] == "Johnathan Doe"
    assert customer["Age"] == 35

    # Attempt to update a non-existing customer
    response = update_customer("nonexistent", full_name="New Name")
    assert response == {"error": "Customer not found"}


def test_delete_customer(test_app):
    # Delete an existing customer
    response = delete_customer("johndoe")
    assert response == {"message": "Customer deleted successfully"}

    # Verify deletion
    customer = get_customer_by_username("johndoe")
    assert customer is None

    # Attempt to delete a non-existing customer
    response = delete_customer("nonexistent")
    assert response == {"error": "Customer not found"}


def test_charge_customer(test_app):
    # Add a new customer
    register_customer(
        full_name="Jane Doe",
        username="janedoe",
        password="password",
        age=25,
        address="456 Oak St",
        gender="Female",
        marital_status="Married"
    )

    # Charge the wallet
    response = charge_customer("janedoe", 50.0)
    assert response == {"message": "Customer account charged successfully"}

    # Verify wallet balance
    customer = get_customer_by_username("janedoe")
    assert customer["Wallet"] == 50.0


def test_deduct_money(test_app):
    # Deduct from the wallet
    response = deduct_money("janedoe", 20.0)
    assert response == {"message": "Money deducted from wallet successfully"}

    # Verify wallet balance
    customer = get_customer_by_username("janedoe")
    assert customer["Wallet"] == 30.0

    # Attempt to deduct more than the balance
    response = deduct_money("janedoe", 50.0)
    assert response == {"error": "Insufficient wallet balance"}


def test_get_all_customers(test_app):
    # Ensure the database starts with the previously added customers
    customers = get_all_customers()
    assert len(customers) == 2  # Expecting two customers: "janedoe" and "johndoe"
    
    # Verify the content of the returned data
    usernames = [customer["Username"] for customer in customers]
    assert "admin" in usernames
    assert "janedoe" in usernames

    # Add a new customer and verify the list updates
    register_customer(
        full_name="Alice Smith",
        username="alicesmith",
        password="mypassword",
        age=28,
        address="789 Pine St",
        gender="Female",
        marital_status="Single"
    )

    customers = get_all_customers()
    assert len(customers) == 3  # Now expecting three customers
    usernames = [customer["Username"] for customer in customers]
    assert "alicesmith" in usernames
