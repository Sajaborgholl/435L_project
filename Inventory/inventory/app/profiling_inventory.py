import cProfile
import pstats
from memory_profiler import profile
from app import app
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
        print(f"{method.upper()} {url} - Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"Exception during {method.upper()} {url}: {e}")
        return None


@profile
def profile_inventory():
    with app.test_client() as client:
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Step 1: Setup Prerequisites
        print("Creating an inventory item...")
        safe_request(client, "post", "/inventory", headers=headers_admin, json={
            "name": "Laptop",
            "category": "Electronics",
            "price": 1500.0,
            "description": "A powerful laptop for developers.",
            "stock": 50
        })

        # Step 2: Profile Routes
        print("Fetching inventory...")
        safe_request(client, "get", "/inventory", headers=headers_admin)

        print("Updating an inventory item...")
        safe_request(client, "put", "/inventory/1", headers=headers_admin, json={
            "price": 1400.0,
            "stock": 40
        })

        print("Deducting stock from an inventory item...")
        safe_request(client, "post", "/inventory/2/deduct", headers=headers_admin, json={
            "count": 5
        })

        print("Deleting an inventory item...")
        safe_request(client, "delete", "/inventory/1", headers=headers_admin)


if __name__ == "__main__":
    # Performance Profiling
    profiler = cProfile.Profile()
    profiler.enable()

    # Run Memory and Function Profiling
    profile_inventory()

    profiler.disable()

    # Generate and Print Stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)
