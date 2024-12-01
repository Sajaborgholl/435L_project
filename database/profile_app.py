import cProfile
from app import app
import pstats
from utils import generate_jwt

# Generate tokens
admin_token = generate_jwt("admin", 1)  # Admin user
user_token = generate_jwt("johndoe", 0)  # Regular user

def safe_request(client, method, url, headers=None, **kwargs):
    """
    Safely perform a request and log errors if any.
    """
    try:
        response = getattr(client, method)(url, headers=headers, **kwargs)
    except Exception as e:
        print(f"Exception during {method.upper()} {url}: {e}")
        return None

def profile_app():
    with app.test_client() as client:
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Step 1: Setup prerequisites
        print("Creating a customer...")
        safe_request(client, "post", "/db/customers", headers=headers_admin, json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Elm St",
            "gender": "Male",
            "marital_status": "Single"
        })

        print("Charging a customer's wallet...")
        safe_request(client, "post", "/db/customers/johndoe/charge", headers=headers_admin, json={
            "amount": 1000.0
        })

        print("Creating an inventory item...")
        safe_request(client, "post", "/db/inventory", headers=headers_admin, json={
            "name": "Laptop",
            "category": "Electronics",
            "price": 999.99,
            "description": "A high-end laptop",
            "stock": 10
        })

        # Step 2: Profile routes

        # Customers
        print("Fetching customers...")
        safe_request(client, "get", "/db/customers", headers=headers_admin)

        print("Fetching a specific customer...")
        safe_request(client, "get", "/db/customers/johndoe", headers=headers_admin)

        print("Updating a customer...")
        safe_request(client, "put", "/db/customers/johndoe", headers=headers_admin, json={
            "address": "789 Pine St"
        })

        print("Deducting money from a customer's wallet...")
        safe_request(client, "post", "/db/customers/johndoe/deduct", headers=headers_admin, json={
            "amount": 20.0
        })
        
        print("Deleting a customer...")
        safe_request(client, "delete", "/db/customers/johndoe", headers=headers_admin)

        # Inventory
        print("Fetching inventory...")
        safe_request(client, "get", "/db/inventory", headers=headers_admin)

        print("Updating an inventory item...")
        safe_request(client, "put", "/db/inventory/1", headers=headers_admin, json={
            "price": 899.99
        })

        print("Deducting stock from an inventory item...")
        safe_request(client, "post", "/db/inventory/10/deduct", headers=headers_admin, json={
            "count": 1
        })

        print("Deleting an inventory item...")
        safe_request(client, "delete", "/db/inventory/1", headers=headers_admin)

        # Sales
        safe_request(client, "post", "/db/inventory", headers=headers_admin, json={
            "name": "Phone",
            "category": "Electronics",
            "price": 500.0,
            "description": "A smartphone",
            "stock": 5
        })
        safe_request(client, "post", "/db/customers", headers=headers_admin, json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Elm St",
            "gender": "Male",
            "marital_status": "Single"
        })
        safe_request(client, "post", "/db/customers/johndoe/charge", headers=headers_admin, json={
            "amount": 2000.0
        })
        print("Creating a sale...")
        safe_request(client, "post", "/db/sales", headers=headers_user, json={
            "product_id": 3,
            "quantity": 1
        })

        print("Fetching all sales...")
        safe_request(client, "get", "/db/sales", headers=headers_admin)

        print("Fetching goods for sale...")
        safe_request(client, "get", "/db/sales/goods", headers=headers_user)

        print("Fetching a specific good...")
        safe_request(client, "get", "/db/sales/good/3", headers=headers_user)

        print("Fetching customer purchases...")
        safe_request(client, "get", "/db/sales/customer/johndoe", headers=headers_user)

        print("Adding to wishlist...")
        safe_request(client, "post", "/db/sales/wishlist/johndoe", headers=headers_user, json={
            "product_id": 3
        })

        print("Fetching wishlist...")
        safe_request(client, "get", "/db/sales/wishlist/johndoe", headers=headers_user)

        print("Fetching recommendations...")
        safe_request(client, "get", "/recommendations/johndoe", headers=headers_user)

        #Reviews
        print("Submitting a review...")
        safe_request(client, "post", "/reviews", headers=headers_user, json={
            "product_id": 10,
            "rating": 5,
            "comment": "Great product!"
        })

        print("Fetching product reviews...")
        safe_request(client, "get", "/reviews/product/10", headers=headers_user)

        print("Fetching customer reviews...")
        safe_request(client, "get", "/reviews/customer/johndoe", headers=headers_user)
        

        print("Updating a review...")
        safe_request(client, "put", "/reviews/1", headers=headers_user, json={
            "rating": 4,
            "comment": "Good product!"
        })

        print("Moderating a review...")
        safe_request(client, "put", "/reviews/1/moderate", headers=headers_admin, json={
            "status": "Approved"
        })

        print("Fetching review details...")
        safe_request(client, "get", "/reviews/1", headers=headers_user)

        print("Deleting a review...")
        safe_request(client, "delete", "/reviews/1", headers=headers_user)

        
if __name__ == "__main__":
    # Run the profiler
    profiler = cProfile.Profile()
    profiler.enable()

    profile_app()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(20)
