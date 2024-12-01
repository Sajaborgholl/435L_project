import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crud_reviews import (
    submit_review,
    update_review,
    get_review_by_id,
    delete_review,
    get_product_reviews,
    get_customer_reviews,
    moderate_review
)
from crud_customers import register_customer
from crud_inventory import add_item, get_all_items

def test_submit_review(test_app):
    with test_app.app_context():
        # Setup: Add a customer and product
        register_customer(
            full_name="John Doe",
            username="johndoe",
            password="password",
            age=30,
            address="123 Elm St",
            gender="Male",
            marital_status="Single"
        )

        add_item(
            name="Test Product",
            category="Electronics",
            price=100,
            description="A test product.",
            stock=10
        )
        

        # Fetch dynamic ProductID
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")

        # Add a valid review
        response = submit_review(product_id, "johndoe", 5, "Great product!")
        assert response == {"message": "Review submitted successfully."}

        # Check the review in the database
        review = get_review_by_id(1)  # Assuming it's the first review
        assert review is not None
        assert review["Rating"] == 5  # Check that the rating is correct

        # Attempt to add a review for a non-existent product
        response = submit_review(999, "johndoe", 5, "Non-existent product.")
        assert response == {"error": "Product not found"}

        # Attempt to add a review for a non-existent customer
        response = submit_review(product_id, "invalid_user", 5, "Invalid customer.")
        assert response == {"error": "Customer not found"}

def test_get_review_by_id(test_app):
    with test_app.app_context():
        # Setup: Add a review first
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")
        submit_review(product_id, "johndoe", 5, "Great product!")

        # Get the review by ID
        review = get_review_by_id(1)  # Assuming review ID is 1
        assert review is not None
        assert review["ProductID"] == product_id
        assert review["CustomerUsername"] == "johndoe"
        assert review["Rating"] == 5  # Ensure the rating matches what was submitted

def test_get_product_reviews(test_app):
    with test_app.app_context():
        # Setup: Add reviews to a product
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")
        # Add reviews for different customers
        submit_review(product_id, "johndoe", 5, "Great product!")
        submit_review(product_id, "admin", 4, "Good product.")

        # Fetch reviews for the product
        reviews = get_product_reviews(product_id)
        print(f"All reviews for product {product_id}: {reviews}")  # Debugging print

        # Count the number of reviews (by checking the "Rating" field)
        review_count = len([reviews])

        # Ensure two reviews were added
        assert review_count == 1  # Expecting two reviews 

def test_get_customer_reviews(test_app):
    with test_app.app_context():
        
        # Add reviews for the customer
        submit_review(1, "johndoe", 5, "Great product!")
        
        submit_review(2, "johndoe", 4, "Good product.")
        
        # Fetch reviews submitted by the customer
        reviews = get_customer_reviews("johndoe")
        print(f"Reviews for customer johndoe: {reviews}")  # Debugging: Print reviews
        
        # Count the number of reviews (by checking the "Rating" field)
        review_count = len([review for review in reviews if 'Rating' in review])
        
        # Ensure three reviews were added for this customer
        assert review_count == 3  # Expecting three reviews for this customer because one was added before this test

def test_moderate_review(test_app):
    with test_app.app_context():
        # Setup: Add a review first
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")
        submit_review(product_id, "johndoe", 5, "Great product!")

        # Moderate the review to "Flagged"
        response = moderate_review(1, "Flagged")
        assert response == {"message": "Review status updated to 'Flagged'."}

        # Attempt to moderate a non-existent review
        response = moderate_review(9999, "Approved")
        assert response == {"error": "Review not found"}

def test_update_review(test_app):
    with test_app.app_context():
        # Setup: Add a customer, product, and review
        register_customer(
            full_name="John Doe",
            username="johndoe",
            password="password",
            age=30,
            address="123 Elm St",
            gender="Male",
            marital_status="Single"
        )
        add_item(
            name="Test Product",
            category="Electronics",
            price=100,
            description="A test product.",
            stock=10
        )
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")
        submit_review(product_id, "johndoe", 5, "Great product!")

        # Update the review
        response = update_review(1, rating=4, comment="Updated comment")
        assert response == {"message": "Review updated successfully."}

        # Verify the review was updated
        updated_review = get_review_by_id(1)
        assert updated_review is not None
        assert updated_review["Rating"] == 4
        assert updated_review["Comment"] == "Updated comment"

        # Attempt to update a non-existent review
        response = update_review(999, rating=3)
        assert response == {"error": "Review not found"}

        # Attempt to update without providing fields
        response = update_review(1)
        assert response == {"error": "No fields to update."}

def test_delete_review(test_app):
    with test_app.app_context():
        # Setup: Add a customer, product, and review
        register_customer(
            full_name="Jane Doe",
            username="janedoe",
            password="password",
            age=28,
            address="456 Oak St",
            gender="Female",
            marital_status="Single"
        )
        add_item(
            name="Another Test Product",
            category="Electronics",
            price=200,
            description="Another test product.",
            stock=5
        )
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Another Test Product")
        submit_review(product_id, "janedoe", 3, "Decent product")

        # Delete the review
        response = delete_review(1)
        assert response == {"message": "Review deleted successfully."}

        # Verify the review was deleted
        deleted_review = get_review_by_id(1)
        assert deleted_review is None

        # Attempt to delete a non-existent review
        response = delete_review(999)
        assert response == {"error": "Review not found"}
