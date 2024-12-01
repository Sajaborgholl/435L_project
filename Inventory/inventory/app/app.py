from flask import Flask, request, jsonify
import requests
try:
    from .utils import generate_jwt, jwt_required
except ImportError:
    from utils import generate_jwt, jwt_required


app = Flask(__name__)


# URL for the Database Service
DATABASE_SERVICE_URL = "http://localhost:5001/db/inventory"


@app.route('/inventory', methods=['GET'])
@jwt_required()
def fetch_inventory():
    """
    Retrieve all inventory items.

    This endpoint forwards the request to the Database service.

    Returns:
        Response: JSON response containing a list of inventory items or an error message.
    """
    # Extract the Authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    try:
        # Forward the request to the Database Service with the Authorization token
        headers = {"Authorization": token}
        response = requests.get(DATABASE_SERVICE_URL, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/inventory', methods=['POST'])
# Enforce token validation in the Inventory Service
@jwt_required(admin_only=True)
def create_item():
    """
    Create a new inventory item by forwarding the request to the Database service.

    **Request JSON Parameters**:
        - `name` (str): The name of the item (required).
        - `category` (str): The category of the item (e.g., food, clothes, accessories, electronics) (required).
        - `price` (float): The price of the item (required).
        - `description` (str): A brief description of the item (required).
        - `stock` (int): The number of items available in stock (required).

    **Responses**:
        - `201 Created`: If the item is successfully created.
        - `400 Bad Request`: If required fields are missing or invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service or invalid response is received.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'category', 'price', 'description', 'stock']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Extract token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the request to the Database service, including the token in the headers
        response = requests.post(
            DATABASE_SERVICE_URL,
            json=data,
            headers={"Authorization": token}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/inventory/<int:item_id>', methods=['PUT'])
# Enforce token validation in the Inventory Service
@jwt_required(admin_only=True)
def modify_item(item_id):
    """
    Update fields for a specific inventory item by forwarding the request to the Database service.

    **Path Parameter**:
        - `item_id` (int): The ID of the inventory item to be updated (required).

    **Request JSON Parameters**:
        - Key-value pairs for the fields to be updated. At least one field must be provided.

    **Responses**:
        - `200 OK`: If the item is successfully updated.
        - `400 Bad Request`: If no data is provided or the request is invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the request to the Database service, including the token in the headers
        response = requests.put(
            f"{DATABASE_SERVICE_URL}/{item_id}",
            json=data,
            headers={"Authorization": token}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/inventory/<int:item_id>/deduct', methods=['POST'])
# Enforce token validation in the Inventory Service
@jwt_required(admin_only=True)
def deduct_stock_from_item(item_id):
    """
    Deduct stock for a specific item in the inventory by forwarding the request to the Database service.

    **Path Parameter**:
        - `item_id` (int): The ID of the inventory item for which stock is to be deducted (required).

    **Request JSON Parameters**:
        - `count` (int): The number of items to deduct from the stock (required).

    **Responses**:
        - `200 OK`: If the stock deduction is successful.
        - `400 Bad Request`: If the `count` field is missing or invalid.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    data = request.get_json()

    if 'count' not in data:
        return jsonify({"error": "Missing 'count' field"}), 400

    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the request to the Database service, including the token in the headers
        response = requests.post(
            f"{DATABASE_SERVICE_URL}/{item_id}/deduct",
            json=data,
            headers={"Authorization": token}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
@jwt_required(admin_only=True)  # Enforce admin-only access
def remove_item(item_id):
    """
    Delete an inventory item by ID by forwarding the request to the Database service.

    **Path Parameter**:
        - `item_id` (int): The ID of the inventory item to be deleted (required).

    **Responses**:
        - `200 OK`: If the item is successfully deleted.
        - `400 Bad Request`: If the provided `item_id` is invalid.
        - `401 Unauthorized`: If the authorization token is missing or invalid.
        - `403 Forbidden`: If the user lacks admin privileges.
        - `500 Internal Server Error`: If there is an issue communicating with the Database service.
    """
    # Extract the authorization token from the incoming request
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the delete request to the Database Service, including the token in headers
        response = requests.delete(
            f"{DATABASE_SERVICE_URL}/{item_id}",
            headers={"Authorization": token}
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500
    except ValueError:
        return jsonify({"error": "Invalid response from Database service."}), 500


if __name__ == '__main__':
    # Start the Inventory service on port 5003
    app.run(host='0.0.0.0', port=5003, debug=True)
