from flask import Flask, request, jsonify
from crud_customers import (
    register_customer,
    delete_customer,
    update_customer,
    get_all_customers,
    get_customer_by_username,
    charge_customer,
    deduct_money
)

app = Flask(__name__)

# Register a New Customer
@app.route('/db/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    if not all(key in data for key in ['full_name', 'username', 'password', 'age', 'address', 'gender', 'marital_status']):
        return jsonify({"error": "Missing required fields"}), 400

    response = register_customer(
        data['full_name'], data['username'], data['password'], data['age'],
        data['address'], data['gender'], data['marital_status']
    )
    if response == "Username already taken":
        return jsonify({"error": response}), 409  # Conflict
    return jsonify({"message": response}), 201  # Created


# Delete a Customer by Username
@app.route('/db/customers/<username>', methods=['DELETE'])
def remove_customer(username):
    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    response = delete_customer(username)
    return jsonify({"message": response}), 200


# Update Customer Information
@app.route('/db/customers/<username>', methods=['PUT'])
def modify_customer(username):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    response = update_customer(username, **data)
    return jsonify({"message": response}), 200


# Get All Customers
@app.route('/db/customers', methods=['GET'])
def fetch_all_customers():
    customers = get_all_customers()
    customers_list = [dict(customer) for customer in customers]
    return jsonify(customers_list), 200


# Get a Single Customer by Username
@app.route('/db/customers/<username>', methods=['GET'])
def fetch_customer(username):
    customer = get_customer_by_username(username)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(dict(customer)), 200


# Charge Customer Wallet
@app.route('/db/customers/<username>/charge', methods=['POST'])
def add_money_to_wallet(username):
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
    return jsonify({"message": response}), 200


# Deduct Money from Wallet
@app.route('/db/customers/<username>/deduct', methods=['POST'])
def subtract_money_from_wallet(username):
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
    return jsonify({"message": response}), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)