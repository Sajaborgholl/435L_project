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
        # print(f"{method.upper()} {url} - Status: {response.status_code}")
        # return response
    except Exception as e:
        print(f"Exception during {method.upper()} {url}: {e}")
        return None


@profile
def profile_sales():
    with app.test_client() as client:
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Step 2: Profile routes
        print("Creating a sale...")
        safe_request(client, "post", "/sales", headers=headers_user, json={

            "product_id": 1,
            "quantity": 1
        })

        print("Fetching all sales...")
        safe_request(client, "get", "/sales", headers=headers_admin)

        print("Fetching goods for sale...")
        safe_request(client, "get", "/sales/goods", headers=headers_user)

        print("Fetching a specific good...")
        safe_request(client, "get", "/sales/good/2", headers=headers_user)

        print("Fetching customer purchases...")
        safe_request(client, "get", "/sales/customer/johndoe",
                     headers=headers_user)

        print("Adding to wishlist...")
        safe_request(client, "post", "/sales/wishlist/johndoe", headers=headers_user, json={
            "product_id": 1
        })

        print("Fetching wishlist...")
        safe_request(client, "get", "/sales/wishlist/johndoe",
                     headers=headers_user)

        print("Fetching recommendations...")
        safe_request(client, "get", "/sales/recommendations/johndoe",
                     headers=headers_user)


if __name__ == "__main__":
    # Performance Profiling
    profiler = cProfile.Profile()
    profiler.enable()

    # Run Memory and Functional Profiling
    profile_sales()

    profiler.disable()

    # Generate and Print Stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)
