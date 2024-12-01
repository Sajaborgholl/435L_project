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
def profile_reviews():
    with app.test_client() as client:
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_user = {"Authorization": f"Bearer {user_token}"}

        # Step 1: Profile review creation
        print("Submitting a new review...")
        safe_request(client, "post", "/reviews", headers=headers_user, json={
            "product_id": 1,
            "rating": 5,
            "comment": "Great product!"
        })

        # Step 2: Modify a review
        print("Modifying an existing review...")
        safe_request(client, "put", "/reviews/4", headers=headers_admin, json={
            "rating": 4,
            "comment": "Updated review comment"
        })

        # Step 3: Fetch product reviews
        print("Fetching reviews for a product...")
        safe_request(client, "get", "/reviews/product/1", headers=headers_user)

        # Step 4: Fetch customer reviews
        print("Fetching reviews by a customer...")
        safe_request(client, "get", f"/reviews/customer/johndoe",
                     headers=headers_admin)

        # Step 5: Moderate a review (admin only)
        print("Moderating a review...")
        safe_request(client, "put", "/reviews/1/moderate", headers=headers_admin, json={
            "status": "Approved"
        })

        # Step 6: Fetch review details
        print("Fetching review details...")
        safe_request(client, "get", "/reviews/4", headers=headers_admin)

        # Step 7: Delete a review
        print("Deleting a review...")
        safe_request(client, "delete", "/reviews/4", headers=headers_admin)


if __name__ == "__main__":
    # Performance Profiling
    profiler = cProfile.Profile()
    profiler.enable()

    # Run Memory and Functional Profiling
    profile_reviews()

    profiler.disable()

    # Generate and Print Stats
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)
