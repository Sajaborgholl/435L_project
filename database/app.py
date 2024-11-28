from flask import Flask, request, jsonify
from initialize_db import initialize_db
from crud_customers import (
    register_customer,
    delete_customer,
    update_customer,
    get_all_customers,
    get_customer_by_username,
    charge_customer,
    deduct_money
)
from crud_inventory import add_item, deduct_item, update_item, get_all_items, delete_item

app = Flask(__name__)

@app.before_request
def before_request():
    # Ensure the app uses the correct database path
    app.config['DATABASE'] = app.config.get('DATABASE', 'ecommerce.db')

"""
Flask Application for Customer Database Service

This module defines RESTful API endpoints for managing customers in the database.
It provides functionality for registering customers, updating their information,
retrieving customer details, and managing wallet balances.

Endpoints:
    - POST /db/customers: Register a new customer.
    - DELETE /db/customers/<username>: Delete a customer by username.
    - PUT /db/customers/<username>: Update customer information.
    - GET /db/customers: Retrieve all customers.
    - GET /db/customers/<username>: Retrieve a single customer by username.
    - POST /db/customers/<username>/charge: Add money to a customer's wallet.
    - POST /db/customers/<username>/deduct: Deduct money from a customer's wallet.
"""

# Register a New Customer
@app.route('/db/customers', methods=['POST'])
def create_customer():
    """
    Register a New Customer

    Accepts a JSON payload with customer details and registers the customer in the database.

    Request Body:
        {
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Elm St",
            "gender": "Male",
            "marital_status": "Single"
        }

    Returns:
        Response (JSON): 
            - A success message with status code 201, or
            - An error message with status code 400/409.
    """
    data = request.get_json()
    if not all(key in data for key in ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']):
        return jsonify({"error": "Missing required fields"}), 400

    response = register_customer(
        data['full_name'], data['username'], data['password'], data['age'],
        data['address'], data['gender'], data['marital_status']
    )
    if response == "Username already taken":
        return jsonify({"error": response}), 409  # Conflict
    return jsonify(response), 201  # Created


# Delete a Customer by Username
@app.route('/db/customers/<username>', methods=['DELETE'])
def remove_customer(username):
    """
    Delete a Customer by Username

    Deletes a customer from the database using their username.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        Response (JSON): A success message with status code 200 or an error message with status code 404.
    """
    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    response = delete_customer(username)
    return jsonify(response), 200


# Update Customer Information
@app.route('/db/customers/<username>', methods=['PUT'])
def modify_customer(username):
    """
    Updates information for an existing customer.

    Args:
        username (str): The username of the customer to update.
        **kwargs: Key-value pairs representing the fields to update.

    Returns:
        dict: 
            - "message" (str): Success message if the update is successful.
            - "error" (str): Error message if the customer does not exist.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    response = update_customer(username, **data)
    return jsonify(response), 200


# Get All Customers
@app.route('/db/customers', methods=['GET'])
def fetch_all_customers():
    """
    Retrieve All Customers

    Retrieves a list of all customers in the database, excluding sensitive information like passwords.

    Returns:
        Response (JSON): A list of customers with status code 200.
    """
    customers = get_all_customers()
    customers_list = [dict(customer) for customer in customers]
    return jsonify(customers_list), 200


# Get a Single Customer by Username
@app.route('/db/customers/<username>', methods=['GET'])
def fetch_customer(username):
    """
    Retrieve a Single Customer by Username

    Retrieves a specific customer's details by their username, excluding sensitive information.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        Response (JSON): The customer's details with status code 200 or an error message with status code 404.
    """
    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(dict(customer)), 200


# Charge Customer Wallet
@app.route('/db/customers/<username>/charge', methods=['POST'])
def add_money_to_wallet(username):
    """
    Charge a Customer's Wallet

    Adds a specified amount of money to a customer's wallet.

    Args:
        username (str): The username of the customer to charge.

    Request Body:
        {
            "amount": 50.0
        }

    Returns:
        Response (JSON): 
            - A success message with status code 200, or
            - An error message with status code 400/404.
    """
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400

    amount = data['amount']
    if amount < 0:
        return jsonify({"error": "Amount cannot be negative"}), 400

    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    response = charge_customer(username, amount)
    return jsonify(response), 200


# Deduct Money from Wallet
@app.route('/db/customers/<username>/deduct', methods=['POST'])
def subtract_money_from_wallet(username):
    """
    Deduct Money from a Customer's Wallet

    Deducts a specified amount of money from a customer's wallet if sufficient funds are available.

    Args:
        username (str): The username of the customer to deduct money from.

    Request Body:
        {
            "amount": 20.0
        }

    Returns:
        Response (JSON): A success message with status code 200 or an error message with status code 400/404.
    """
    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400

    amount = data['amount']
    if amount < 0:
        return jsonify({"error": "Amount cannot be negative"}), 400

    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    # Check if the customer has enough balance
    if customer['Wallet'] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    response = deduct_money(username, amount)
    return jsonify(response), 200


###############################################Inventory#####################################################

@app.route('/db/inventory', methods=['GET'])
def fetch_inventory():
    """
    Retrieve all inventory items.

    Returns:
        Response: JSON object with a list of inventory items.
    """
    items = get_all_items()
    return jsonify(items), 200

@app.route('/db/inventory', methods=['POST'])
def create_item():
    """
    Create a new inventory item.

    Accepts a JSON payload with the following fields:
        - name (str): The name of the item.
        - category (str): The category of the item (e.g., food, clothes, accessories, electronics).
        - price (float): The price per item.
        - description (str): A brief description of the item.
        - stock (int): The count of available items in stock.

    Returns:
        Response: JSON object indicating success or failure.
    """
    data = request.get_json()
    required_fields = ['name', 'category', 'price', 'description', 'stock']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    response = add_item(data['name'], data['category'], data['price'], data['description'], data['stock'])
    return jsonify(response), 201

@app.route('/db/inventory/<int:item_id>', methods=['PUT'])
def modify_item(item_id):
    """
    Update fields for a specific inventory item.

    Args:
        item_id (int): The ID of the item to update.

    Accepts a JSON payload with key-value pairs for the fields to update.

    Returns:
        Response: JSON object indicating success or failure.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    response = update_item(item_id, **data)
    return jsonify(response), 200

@app.route('/db/inventory/<int:item_id>/deduct', methods=['POST'])
def deduct_stock_from_item(item_id):
    """
    Deduct stock for a specific item in the inventory.

    Args:
        item_id (int): The ID of the item to deduct stock from.

    Accepts a JSON payload with the field:
        - count (int): The number of items to deduct.

    Returns:
        Response: JSON object indicating success or failure.
    """
    data = request.get_json()
    if 'count' not in data:
        return jsonify({"error": "Missing 'count' field"}), 400

    response = deduct_item(item_id, data['count'])
    if 'error' in response:
        return jsonify(response), 400
    return jsonify(response), 200

@app.route('/db/inventory/<int:item_id>', methods=['DELETE'])
def remove_item(item_id):
    """
    Delete an inventory item by ID.

    Args:
        item_id (int): The ID of the item to delete.

    Returns:
        Response: JSON object indicating success or failure.
    """
    response = delete_item(item_id)
    return jsonify(response), 200

if __name__ == '__main__':
    initialize_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
