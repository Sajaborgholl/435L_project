import requests
from flask import Flask, request, jsonify
try:
    from .utils import generate_jwt, jwt_required
except ImportError:
    from utils import generate_jwt, jwt_required

app = Flask(__name__)

# URL for the Database Service
DATABASE_SERVICE_URL = "http://database:5001/db/customers"


@app.route('/customers/register', methods=['POST'])
@jwt_required()  # Ensure the request is authenticated
def register_customer():
    """
    Register a new customer.

    This endpoint accepts customer registration data and forwards it to the Database service for storage.

    **Request Body**:
        The request should include the following fields in JSON format:
        - `full_name` (str): Full name of the customer.
        - `username` (str): Unique username for the customer.
        - `password` (str): Password for the customer account (will be hashed).
        - `age` (int): Age of the customer.
        - `address` (str): Address of the customer.
        - `gender` (str): Gender of the customer. Must be one of `Male`, `Female`, or `Other`.
        - `marital_status` (str): Marital status of the customer. Must be one of `Single`, `Married`, `Divorced`, or `Widowed`.

    **Responses**:
        - `201 Created`: If the customer is registered successfully.
        - `400 Bad Request`: If required fields are missing.
        - `500 Internal Server Error`: If the Database service is unavailable.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['full_name', 'username', 'password',
                       'age', 'address', 'gender', 'marital_status']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Extract the authorization token
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Forward the request to the Database service
    try:
        response = requests.post(
            DATABASE_SERVICE_URL,
            json=data,
            headers={"Authorization": token}  # Forward the token
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/customers/<username>', methods=['DELETE'])
@jwt_required(admin_only=True)  # Enforce admin-only access
def delete_customer(username):
    """
    Delete a Customer

    Forwards a request to delete a customer by username to the Database service.

    Args:
        username (str): The username of the customer to be deleted.

    **Responses**:
        - `200 OK`: Customer deleted successfully.
        - `404 Not Found`: Customer not found.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `403 Forbidden`: If the user lacks admin privileges.
        - `500 Internal Server Error`: Database service communication failure.
    """
    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the DELETE request to the Database Service, including the token in headers
        response = requests.delete(
            f"{DATABASE_SERVICE_URL}/{username}",
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/customers/<username>', methods=['PUT'])
@jwt_required(admin_only=True)  # Enforce admin-only access
def update_customer(username):
    """
    Update customer information by forwarding the request to the Database service.

    **Path Parameter**:
        - `username` (str): The username of the customer to update.

    **Request JSON Parameters**:
        Key-value pairs for the fields to update.

    **Responses**:
        - `200 OK`: If the customer information is updated successfully.
        - `400 Bad Request`: If no data is provided or the request is invalid.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `403 Forbidden`: If the user lacks admin privileges.
        - `404 Not Found`: If the customer does not exist.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Validate if data is provided
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Forward the PUT request to the Database Service, including the token in headers
        response = requests.put(
            f"{DATABASE_SERVICE_URL}/{username}",
            json=data,
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/customers/<username>', methods=['GET'])
@jwt_required()  # Enforce authentication
def get_customer(username):
    """
    Retrieve a Single Customer by Username

    Forwards a request to retrieve a specific customer's information from the Database service.

    **Path Parameter**:
        - `username` (str): The username of the customer to retrieve (required).

    **Responses**:
        - `200 OK`: The customer's details.
        - `404 Not Found`: If the customer is not found in the database.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the GET request to the Database Service, including the token in headers
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/{username}",
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/customers', methods=['GET'])
@jwt_required(admin_only=True)  # Enforce admin-only access
def get_all_customers():
    """
    Retrieve All Customers

    Forwards a request to fetch all customers from the Database service.

    **Responses**:
        - `200 OK`: A list of all customers.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `403 Forbidden`: If the user lacks admin privileges.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the GET request to the Database Service, including the token in headers
        response = requests.get(
            DATABASE_SERVICE_URL,
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/customers/<username>/charge', methods=['POST'])
@jwt_required()  # Enforce authentication
def charge_wallet(username):
    """
    Add Money to Wallet

    Forwards a request to add a specified amount of money to a customer's wallet.

    **Path Parameter**:
        - `username` (str): The username of the customer (required).

    **Request Body**:
        - `amount` (float): The amount to add to the customer's wallet (required).

    **Responses**:
        - `200 OK`: If the amount is successfully added to the wallet.
        - `400 Bad Request`: If the `amount` field is missing or invalid.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    data = request.get_json()

    if 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400

    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the POST request to the Database Service, including the token in headers
        response = requests.post(
            f"{DATABASE_SERVICE_URL}/{username}/charge",
            json=data,
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/customers/<username>/deduct', methods=['POST'])
@jwt_required()  # Enforce authentication
def deduct_wallet(username):
    """
    Deduct Money from Wallet

    Forwards a request to deduct a specified amount of money from a customer's wallet.

    **Path Parameter**:
        - `username` (str): The username of the customer (required).

    **Request Body**:
        - `amount` (float): The amount to deduct from the customer's wallet (required).

    **Responses**:
        - `200 OK`: If the amount is successfully deducted from the wallet.
        - `400 Bad Request`: If the `amount` field is missing or invalid.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    data = request.get_json()

    if 'amount' not in data:
        return jsonify({"error": "Amount is required"}), 400

    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the POST request to the Database Service, including the token in headers
        response = requests.post(
            f"{DATABASE_SERVICE_URL}/{username}/deduct",
            json=data,
            headers={"Authorization": token}  # Forward the token
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


if __name__ == '__main__':
    # Start the Customers service on port 5002
    app.run(host='0.0.0.0', port=5002, debug=True)
