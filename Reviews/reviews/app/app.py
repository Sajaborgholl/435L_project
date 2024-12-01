from flask import Flask, request, jsonify
import requests
try:
    from .utils import generate_jwt, jwt_required
except ImportError:
    from utils import generate_jwt, jwt_required

app = Flask(__name__)


# URL for the Database Service
DATABASE_SERVICE_URL = "http://database:5001/reviews"


@app.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    """
    Submit a new review for a product.

    **Expects**:
        - JSON Payload:
            {
                "product_id": int (required),
                "rating": int (1-5, required),
                "comment": str (optional)
            }

    **Returns**:
        - `201 Created`: If the review is successfully created.
        - `400 Bad Request`: If required fields are missing.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    data = request.get_json()
    required_fields = ['product_id', 'rating']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    username = request.user.get("username")
    response = requests.post(
        f"{DATABASE_SERVICE_URL}",
        json={"product_id": data["product_id"],
              "rating": data["rating"], "comment": data.get("comment")},
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def modify_review(review_id):
    """
    Modify an existing review.

    **Expects**:
        - URL Parameter: `review_id` (int) - ID of the review to modify.
        - JSON Payload:
            {
                "rating": int (1-5, optional),
                "comment": str (optional)
            }

    **Returns**:
        - `200 OK`: If the review is successfully updated.
        - `403 Forbidden`: If the user is not authorized to modify the review.
        - `404 Not Found`: If the review does not exist.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    data = request.get_json()
    response = requests.put(
        f"{DATABASE_SERVICE_URL}/{review_id}",
        json={"rating": data.get("rating"), "comment": data.get("comment")},
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def remove_review(review_id):
    """
    Delete a review if the user is the author or an admin.

    **Expects**:
        - URL Parameter: `review_id` (int) - ID of the review to delete.

    **Returns**:
        - `200 OK`: If the review is successfully deleted.
        - `403 Forbidden`: If the user is not authorized to delete the review.
        - `404 Not Found`: If the review does not exist.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    response = requests.delete(
        f"{DATABASE_SERVICE_URL}/{review_id}",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/product/<int:product_id>', methods=['GET'])
@jwt_required()
def fetch_product_reviews(product_id):
    """
    Retrieve all reviews for a specific product.

    **Expects**:
        - URL Parameter: `product_id` (int) - ID of the product.

    **Returns**:
        - `200 OK`: List of reviews for the product.
        - `404 Not Found`: If no reviews are found.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    response = requests.get(
        f"{DATABASE_SERVICE_URL}/product/{product_id}",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/customer/<username>', methods=['GET'])
@jwt_required()
def fetch_customer_reviews(username):
    """
    Retrieve all reviews submitted by a specific customer.

    **Expects**:
        - URL Parameter: `username` (str) - Username of the customer.

    **Returns**:
        - `200 OK`: List of reviews by the customer.
        - `403 Forbidden`: If the user is not authorized to view the reviews.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    response = requests.get(
        f"{DATABASE_SERVICE_URL}/customer/{username}",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/<int:review_id>/moderate', methods=['PUT'])
@jwt_required(admin_only=True)
def moderate_review_status(review_id):
    """
    Moderate a review by updating its status.

    **Expects**:
        - URL Parameter: `review_id` (int) - ID of the review to moderate.
        - JSON Payload:
            {
                "status": str ("Approved" or "Flagged", required)
            }

    **Returns**:
        - `200 OK`: If the status is successfully updated.
        - `400 Bad Request`: If the status is invalid.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    data = request.get_json()
    response = requests.put(
        f"{DATABASE_SERVICE_URL}/{review_id}/moderate",
        json={"status": data["status"]},
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


@app.route('/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
def fetch_review_details(review_id):
    """
    Retrieve details for a specific review.

    **Expects**:
        - URL Parameter: `review_id` (int) - ID of the review to fetch.

    **Returns**:
        - `200 OK`: Detailed information about the review.
        - `404 Not Found`: If the review does not exist or has been flagged.
        - `500 Internal Server Error`: If an internal error occurs.
    """
    response = requests.get(
        f"{DATABASE_SERVICE_URL}/{review_id}",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return jsonify(response.json()), response.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
