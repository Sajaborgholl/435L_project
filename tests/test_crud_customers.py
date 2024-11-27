import os
import tempfile
from database.crud_customers import (
    register_customer,
    get_all_customers,
    get_customer_by_username,
    update_customer,
    delete_customer,
    charge_customer,
    deduct_money
)
from database.initialize_db import initialize_db
from database.app import app

def test_register_customer():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            response = register_customer(
                "John Doe", "johndoe123", "password123", 30, "123 Elm St", "Male", "Single"
            )
            assert response.get("message") == "Customer registered successfully"
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_get_all_customers():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "John Doe", "johndoe123", "password123", 30, "123 Elm St", "Male", "Single"
            )
            customers = get_all_customers()
            assert len(customers) == 2  # Admin user and John Doe
            usernames = [customer["Username"] for customer in customers]
            assert "johndoe123" in usernames
            assert "admin" in usernames
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_get_customer_by_username():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "Alice Smith", "alicesmith", "password456", 25, "456 Oak St", "Female", "Single"
            )
            customer = get_customer_by_username("alicesmith")
            assert customer is not None
            assert customer["FullName"] == "Alice Smith"
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_update_customer():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "Bob Johnson", "bobjohnson", "password789", 40, "789 Pine St", "Male", "Married"
            )
            response = update_customer("bobjohnson", full_name="Robert Johnson", age=41)
            assert response.get("message") == "Customer updated successfully"
            customer = get_customer_by_username("bobjohnson")
            assert customer["FullName"] == "Robert Johnson"
            assert customer["Age"] == 41
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_delete_customer():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "Carol Williams", "carolw", "password101", 35, "246 Maple St", "Female", "Married"
            )
            response = delete_customer("carolw")
            assert response.get("message") == "Customer deleted successfully"
            customer = get_customer_by_username("carolw")
            assert customer is None
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_charge_customer():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "David Lee", "davidl", "password202", 28, "135 Cedar St", "Male", "Single"
            )
            response = charge_customer("davidl", 100.0)
            assert response.get("message") == "Customer account charged successfully"
            customer = get_customer_by_username("davidl")
            assert customer["Wallet"] == 100.0
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_deduct_money():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "Eve Adams", "evea", "password303", 22, "864 Birch St", "Female", "Single"
            )
            charge_customer("evea", 50.0)
            response = deduct_money("evea", 30.0)
            assert response.get("message") == "Money deducted from wallet successfully"
            customer = get_customer_by_username("evea")
            assert customer["Wallet"] == 20.0
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)


def test_deduct_money_insufficient_balance():
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    try:
        with app.app_context():
            app.config['DATABASE'] = temp_db_path
            initialize_db(temp_db_path)
            register_customer(
                "Frank Miller", "frankm", "password404", 30, "753 Spruce St", "Male", "Single"
            )
            response = deduct_money("frankm", 10.0)
            assert response.get("error") == "Insufficient wallet balance"
    finally:
        os.close(temp_db_fd)
        os.remove(temp_db_path)