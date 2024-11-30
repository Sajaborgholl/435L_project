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

from crud_sales import record_sale, fetch_sales, get_goods, get_specific_goods, get_customer_purchases, add_to_wishlist, fetch_wishlist, recommend_products

from crud_reviews import (
    submit_review,
    update_review,
    delete_review,
    get_product_reviews,
    get_customer_reviews,
    moderate_review,
    get_review_details,
    get_review_by_id
)

from utils import generate_jwt, jwt_required
from werkzeug.security import check_password_hash

app = Flask(__name__)

@app.before_request
def before_request():
    # Ensure the app uses the correct database path
    app.config['DATABASE'] = app.config.get('DATABASE', 'ecommerce.db')

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and issue a JWT token.

    Request Body:
        {
            "username": "user1",
            "password": "password123"
        }

    Returns:
        Response: JSON with JWT token if successful, error message otherwise.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    customer = get_customer_by_username(username)
    if not customer or not check_password_hash(customer["Password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    token = generate_jwt(customer["Username"], customer["UserRole"])
    return jsonify({"token": token}), 200


################################################Customer##################################################
# Register a New Customer
@app.route('/db/customers', methods=['POST'])
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
def fetch_inventory():
    """
    Retrieve all inventory items.

    Returns:
        Response: JSON object with a list of inventory items.
    """
    items = get_all_items()
    return jsonify(items), 200

@app.route('/db/inventory', methods=['POST'])
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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
@jwt_required(admin_only=True)
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


############################################################Sales####################################################

@app.route('/db/sales', methods=['POST'])
@jwt_required()
def create_sale():
    """
    Create a new sale record.

    Expects:
        JSON payload with 'customer_username', 'product_id', and 'quantity'.

    Returns:
        Response: JSON object indicating success or failure message.
    """
    user = request.user  # Added by `jwt_required` decorator
    data = request.get_json()
    customer_username = user.get('username')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not all([customer_username, product_id, quantity]):
        return jsonify({"error": "Missing fields"}), 400

    response = record_sale(customer_username, product_id, quantity)
    if "error" in response:
        return jsonify(response), 400

    return jsonify(response), 201

# Fetch all sales
@app.route('/db/sales', methods=['GET'])
@jwt_required(admin_only=True)
def get_sales():
    """
    Retrieve all sales records.

    Returns:
        Response: JSON object containing a list of sales.
    """
    sales = fetch_sales()
    return jsonify(sales), 200

@app.route('/db/sales/goods', methods=['GET'])
@jwt_required()
def get_goods_sales():
    """
    Retrieve available goods for sale.

    Returns:
        Response: JSON object containing a list of goods, including their names and prices.
    """
    goods = get_goods()
    return jsonify(goods), 200

@app.route('/db/sales/good/<int:product_id>', methods=['GET'])
@jwt_required()
def get_specific_good(product_id):
    """
    Retrieve full details of a specific good.

    Args:
        product_id (int): The ID of the product to retrieve.

    Returns:
        Response: JSON object containing detailed information about the product,
                  or an error message if the product is not found.
    """
    product = get_specific_goods(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200

@app.route('/db/sales/customer/<username>', methods=['GET'])
@jwt_required()
def get_purchases(username):
    """
    Retrieve all historical purchases of a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: JSON object containing a list of purchases made by the customer.
    """
    user = request.user  # Added by `jwt_required` decorator
    if user.get("username") != username and user.get("user_role") != 1:
        return jsonify({"error": "Permission denied"}), 403

    purchases = get_customer_purchases(username)
    return jsonify(purchases), 200

@app.route('/db/sales/wishlist/<username>', methods=['POST'])
@jwt_required()
def add_to_user_wishlist(username):
    """
    Add a product to the customer's wishlist.

    Args:
        username (str): The username of the customer.

    Request Body:
        {
            "product_id": int  # The ID of the product to add to the wishlist.
        }

    Returns:
        Response: JSON object indicating success or failure.
    """
    user = request.user  # Added by `jwt_required` decorator
    if user.get("username") != username and user.get("user_role") != 1:
        return jsonify({"error": "Permission denied"}), 403
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    response = add_to_wishlist(username, product_id)
    return jsonify(response), 200

@app.route('/db/sales/wishlist/<username>', methods=['GET'])
@jwt_required()
def get_user_wishlist(username):
    """
    Retrieve the wishlist of a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: JSON object containing a list of products in the customer's wishlist.
    """
    user = request.user  # Added by `jwt_required` decorator
    if user.get("username") != username and user.get("user_role") != 1:
        return jsonify({"error": "Permission denied"}), 403
    wishlist = fetch_wishlist(username)
    return jsonify(wishlist), 200

@app.route('/recommendations/<username>', methods=['GET'])
@jwt_required()
def get_recommendations(username):
    """
    Fetch recommendations for a customer based on purchase history.

    Args:
        username (str): The username of the customer.

    Returns:
        Response: JSON object containing a list of recommended products.
    """
    user = request.user  # Added by `jwt_required` decorator
    if user.get("username") != username and user.get("user_role") != 1:
        return jsonify({"error": "Permission denied"}), 403
    recommendations = recommend_products(username)
    if not recommendations:
        return jsonify({"message": "No recommendations available."}), 200
    return jsonify(recommendations), 200

##############################################Reviews####################################################

@app.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """
    Submits a new review for a product.

    This endpoint allows a customer to submit a review with a rating and optional comment for a specific product.

    Request Body:
        {
            "product_id": int,
            "rating": int (1-5),
            "comment": str (optional)
        }

    Returns:
        Response (JSON):
            - Success message with status code 201, or
            - Error message with status code 400 if required fields are missing.
    """
    data = request.get_json()
    required_fields = ['product_id', 'rating']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    user = request.user  # Added by `jwt_required` decorator
    username = user.get("username")
    response = submit_review(data['product_id'], username, data['rating'], data.get('comment'))
    return jsonify(response), 201

@app.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def modify_review(review_id):
    """
    Modify an existing review.
    This endpoint allows a user to modify a review identified by its ID. The user must be authenticated
    and authorized to modify the review. Only the user who created the review or an admin can modify it.
    Args:
        review_id (int): The ID of the review to be modified.
    Returns:
        Response: A JSON response containing the updated review data if successful, or an error message
        with the appropriate HTTP status code if the review is not found or the user is not authorized.
    Raises:
        404: If the review with the specified ID is not found.
        403: If the user is not authorized to modify the review.
    """
    user = request.user  # Added by `jwt_required` decorator
    username = user.get("username")
    user_role = user.get("user_role")

    review = get_review_by_id(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    
    if review["CustomerUsername"] != username and user_role != 1:
        return jsonify({"error": "Permission denied"}), 403
    
    data = request.get_json()
    response = update_review(review_id, data.get('rating'), data.get('comment'))
    return jsonify(response), 200

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def remove_review(review_id):
    """
    Deletes a review if the user is the author or an admin.

    Args:
        review_id (int): ID of the review.

    Returns:
        Response: JSON message indicating success or error.
    """
    # Retrieve the user's role and username from the JWT
    user = request.user  # Added by `jwt_required` decorator
    username = user.get("username")
    user_role = user.get("user_role")

    # Fetch the review details to check ownership or admin privileges
    review = get_review_by_id(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    # Check if the user is the review author or an admin
    if review["CustomerUsername"] != username and user_role != 1:
        return jsonify({"error": "Permission denied"}), 403

    # Perform the deletion
    response = delete_review(review_id)
    return jsonify(response), 200

@app.route('/reviews/product/<int:product_id>', methods=['GET'])
@jwt_required()
def fetch_product_reviews(product_id):
    """
    Retrieves all reviews for a specific product.

    This endpoint fetches all reviews associated with a given product ID, filtered by a status of 'Pending' or 'Approved'.

    Args:
        product_id (int): The ID of the product for which reviews are being retrieved.

    Returns:
        Response (JSON): A list of reviews with status code 200.
    """
    reviews = get_product_reviews(product_id)
    return jsonify(reviews), 200

@app.route('/reviews/customer/<username>', methods=['GET'])
@jwt_required()
def fetch_customer_reviews(username):
    """
    Retrieves all reviews submitted by a specific customer.

    This endpoint fetches all reviews written by a customer, identified by their username, filtered by a status of 'Pending' or 'Approved'.

    Args:
        username (str): The username of the customer whose reviews are being retrieved.

    Returns:
        Response (JSON): A list of reviews with status code 200.
    """
    user = request.user  # Added by `jwt_required` decorator
    if user.get("username") != username and user.get("user_role") != 1:
        return jsonify({"error": "Permission denied"}), 403
    reviews = get_customer_reviews(username)
    return jsonify(reviews), 200

@app.route('/reviews/<int:review_id>/moderate', methods=['PUT'])
@jwt_required(admin_only=True)
def moderate_review_status(review_id):
    """
    Moderates a review by updating its status.

    This endpoint allows an administrator to change the status of a review to either 'Approved' or 'Flagged'.

    Args:
        review_id (int): The ID of the review to be moderated.

    Request Body:
        {
            "status": str (e.g., 'Approved', 'Flagged')
        }

    Returns:
        Response (JSON):
            - Success message with status code 200, or
            - Error message with status code 400 if an invalid status is provided.
    """
    data = request.get_json()
    response = moderate_review(review_id, data.get('status'))
    return jsonify(response), 200

@app.route('/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
def fetch_review_details(review_id):
    """
    Retrieves details for a specific review.

    This endpoint fetches detailed information about a review, such as the product ID, customer username, rating, comment, and timestamp.

    Args:
        review_id (int): The ID of the review to retrieve.

    Returns:
        Response (JSON):
            - Review details with status code 200, or
            - Error message with status code 404 if the review is not found or flagged.
    """
    review = get_review_details(review_id)
    if not review:
        return jsonify({"error": "Review not found or has been flagged by Admin"}), 404
    return jsonify(review), 200

if __name__ == '__main__':
    initialize_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
