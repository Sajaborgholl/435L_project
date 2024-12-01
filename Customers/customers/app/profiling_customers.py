import cProfile
import pstats
from app import app
from utils import generate_jwt
from memory_profiler import profile

# Generate tokens
admin_token = generate_jwt("admin", 1)  # Admin user
user_token = generate_jwt("johndoe", 0)  # Regular user


def safe_request(client, method, url, headers=None, **kwargs):
    """
    Safely perform a request and log errors if any.
    """
    try:
        response = getattr(client, method)(url, headers=headers, **kwargs)
        print(f"{method.upper()} {url} - Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"Exception during {method.upper()} {url}: {e}")
        return None


@profile
def profile_customers():
    with app.test_client() as client:
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Step 1: Setup prerequisites
        print("Registering a customer...")
        safe_request(client, "post", "/customers/register", headers=headers_admin, json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Elm St",
            "gender": "Male",
            "marital_status": "Single"
        })

        print("Charging a customer's wallet...")
        safe_request(client, "post", "/customers/johndoe/charge", headers=headers_admin, json={
            "amount": 500.0
        })

        # Step 2: Profile routes

        # Customers
        print("Fetching all customers (admin only)...")
        safe_request(client, "get", "/customers", headers=headers_admin)

        print("Fetching a specific customer...")
        safe_request(client, "get", "/customers/johndoe",
                     headers=headers_admin)

        print("Updating a customer's details...")
        safe_request(client, "put", "/customers/johndoe", headers=headers_admin, json={
            "address": "789 Pine St",
            "age": 31
        })

        print("Deducting from a customer's wallet...")
        safe_request(client, "post", "/customers/johndoe/deduct", headers=headers_admin, json={
            "amount": 100.0
        })

        print("Deleting a customer (admin only)...")
        safe_request(client, "delete", "/customers/johndoe",
                     headers=headers_admin)


if __name__ == "__main__":
    # Run the profiler
    profiler = cProfile.Profile()
    profiler.enable()

    profile_customers()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(20)
