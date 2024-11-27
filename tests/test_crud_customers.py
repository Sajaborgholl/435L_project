import random
from database.crud_customers import (
    register_customer,
    get_all_customers,
    get_customer_by_username,
    delete_customer,
    update_customer,
    charge_customer,
    deduct_money
)

def generate_unique_username(base="user"):
    """Generate a unique username for tests."""
    return f"{base}_{random.randint(1000, 9999)}"


def test_register_customer():
    unique_username = generate_unique_username("janedoe")
    response = register_customer("Jane Doe", unique_username, "password123", 28, "456 Maple St", "Female", "Married")
    assert response.get("message") == "Customer registered successfully"


def test_get_all_customers():
    unique_username = generate_unique_username("johndoe")
    register_customer("John Doe", unique_username, "password123", 30, "123 Elm St", "Male", "Single")
    customers = get_all_customers()
    non_admin_customers = [c for c in customers if c['Username'] != 'admin']
    assert len(non_admin_customers) >= 1  # Ensure there is at least one test customer


def test_get_customer_by_username():
    unique_username = generate_unique_username("johndoe")
    register_customer("John Doe", unique_username, "password123", 30, "123 Elm St", "Male", "Single")
    customer = get_customer_by_username(unique_username)
    assert customer["FullName"] == "John Doe"
    assert "Password" not in customer


def test_delete_customer():
    unique_username = generate_unique_username("johndoe")
    register_customer("John Doe", unique_username, "password123", 30, "123 Elm St", "Male", "Single")
    response = delete_customer(unique_username)
    assert response["message"] == "Customer deleted successfully"

    response = delete_customer("nonexistent")
    assert response["error"] == "Customer not found"
