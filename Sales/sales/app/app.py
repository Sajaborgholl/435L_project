from flask import Flask, request, jsonify
import requests
try:
    from .utils import generate_jwt, jwt_required
except ImportError:
    from utils import generate_jwt, jwt_required

app = Flask(__name__)


# URL for the Database Service
DATABASE_SERVICE_URL = "http://database:5001/db/sales"


@app.route('/sales', methods=['POST'])
@jwt_required()
def create_sale():
    """
   Create a New Sale Record

    Forwards a request to create a sale record to the Database Service.

    **Request JSON Parameters**:
        - `customer_username` (str): The username of the customer making the purchase. (Required)
        - `product_id` (int): The ID of the product being purchased. (Required)
        - `quantity` (int): The number of items being purchased. (Required)

    **Headers**:
        - `Authorization` (str): Bearer token for authentication.

    **Response**:
        - `201 Created`: Sale record created successfully.
            ```json
            {
                "message": "Sale recorded successfully",
                "sale_id": 12345
            }
            ```
        - `400 Bad Request`: Missing required fields.
            ```json
            {
                "error": "Missing required fields: customer_username, product_id"
            }
            ```
        - `500 Internal Server Error`: Communication with the Database Service failed.
            ```json
            {
                "error": "Could not communicate with the Database service: <error details>"
            }
            ```.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ['customer_username', 'product_id', 'quantity']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    # Get the token from the incoming request's Authorization header
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Forward the request to the Database Service with the token in headers
        response = requests.post(
            DATABASE_SERVICE_URL,
            json=data,
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales', methods=['GET'])
@jwt_required()
def get_sales():
    """
    Retrieve all sales records.

    Expects:
        - `Authorization` header: Bearer token for authentication.

    Returns:
        - **200 OK**: JSON response containing a list of sales records.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.get(
            DATABASE_SERVICE_URL,
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/goods', methods=['GET'])
@jwt_required()
def get_goods_sales():
    """
    Retrieve available goods for sale.

    Expects:
        - `Authorization` header: Bearer token for authentication.

    Returns:
        - **200 OK**: JSON response containing a list of goods for sale.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/goods",
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/good/<int:product_id>', methods=['GET'])
@jwt_required()
def get_specific_good(product_id):
    """
    Retrieve full details of a specific good.

    Expects:
        - `Authorization` header: Bearer token for authentication.
        - `product_id` (int): The ID of the product to retrieve.

    Returns:
        - **200 OK**: JSON response containing the product's details.
        - **404 Not Found**: If the product is not found.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/good/{product_id}",
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/customer/<username>', methods=['GET'])
@jwt_required()
def get_purchases(username):
    """
    Retrieve all historical purchases of a specific customer.

    Expects:
        - `Authorization` header: Bearer token for authentication.
        - `username` (str): The username of the customer.

    Returns:
        - **200 OK**: JSON response containing the customer's purchase history.
        - **404 Not Found**: If the customer has no purchase history.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/customer/{username}",
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/wishlist/<username>', methods=['POST'])
@jwt_required()
def add_to_user_wishlist(username):
    """
    Add a product to a customer's wishlist.

    Expects:
        - `Authorization` header: Bearer token for authentication.
        - JSON body:
            - `product_id` (int): The ID of the product to add to the wishlist.

    Returns:
        - **200 OK**: JSON response indicating the product was added to the wishlist.
        - **400 Bad Request**: If `product_id` is missing in the request body.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Validate required fields in the request body
    data = request.get_json()
    if 'product_id' not in data:
        return jsonify({"error": "Product ID is required"}), 400

    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.post(
            f"{DATABASE_SERVICE_URL}/wishlist/{username}",
            json=data,
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/wishlist/<username>', methods=['GET'])
@jwt_required()
def get_user_wishlist(username):
    """
    Retrieve a customer's wishlist.

    Expects:
        - `Authorization` header: Bearer token for authentication.
        - Path parameter:
            - `username` (str): The username of the customer.

    Returns:
        - **200 OK**: JSON response containing the wishlist items.
        - **500 Internal Server Error**: If communication with the Database service fails.
    """
    # Extract the authorization token
    token = request.headers.get("Authorization")

    try:
        # Forward the request to the Database service with the token
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/wishlist/{username}",
            headers={"Authorization": token}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


@app.route('/sales/recommendations/<username>', methods=['GET'])
@jwt_required()
def get_recommendations(username):
    """
    Fetch recommendations for a customer by forwarding the request to the Recommendation Service.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: JSON object containing a list of recommended products, 
                  or an appropriate error message.
    """
    token = request.headers.get(
        "Authorization")  # Extract the token from the request headers
    try:
        # Forward the request to the Database/Recommendation Service
        response = requests.get(
            f"{DATABASE_SERVICE_URL}/recommendations/{username}",
            headers={"Authorization": token}  # Pass the token in headers
        )
        response.raise_for_status()  # Raise an error for non-2xx responses
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Could not communicate with the Database service: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
