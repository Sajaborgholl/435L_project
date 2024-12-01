import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crud_sales import (
    record_sale,
    get_goods,
    fetch_sales,
    get_specific_goods,
    get_customer_purchases,
    add_to_wishlist,
    fetch_wishlist,
    recommend_products
)
from crud_customers import register_customer, charge_customer
from crud_inventory import add_item, get_all_items, update_item


def test_record_sale(test_app):
    with test_app.app_context():
        # Setup: Register customer, charge wallet, add item
        register_customer(
            full_name="John Doe",
            username="johndoe",
            password="password",
            age=30,
            address="123 Elm St",
            gender="Male",
            marital_status="Single"
        )
        charge_customer("johndoe", 1000)

        add_item(
            name="Test Product",
            category="Electronics",
            price=100,
            description="A test product.",
            stock=12
        )

        # Fetch dynamic ProductID
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")

        # Successful sale
        response = record_sale("johndoe", product_id, 2)
        assert response == {"message": "Sale recorded successfully"}

        # Insufficient stock
        response = record_sale("johndoe", product_id, 20)
        assert response == {"error": "Insufficient stock"}

        # Insufficient wallet balance
        response = record_sale("johndoe", product_id, 10)  # Exceeds wallet balance
        assert response == {"error": "Insufficient wallet balance"}

        # Invalid product
        response = record_sale("johndoe", 999, 1)
        assert response == {"error": "Product not found"}

        # Invalid customer
        response = record_sale("invalid_user", product_id, 1)
        assert response == {"error": "Customer not found"}


def test_get_goods(test_app):
    with test_app.app_context():
        goods = get_goods()
        assert len(goods) > 0  # Ensure there are goods in inventory
        assert any(item["Name"] == "Test Product" for item in goods)


def test_fetch_sales(test_app):
    with test_app.app_context():
        sales = fetch_sales()
        assert len(sales) > 0  # At least one sale should be recorded
        assert any(sale["CustomerUsername"] == "johndoe" for sale in sales)


def test_get_specific_goods(test_app):
    with test_app.app_context():
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")
        product = get_specific_goods(product_id)
        assert product is not None
        assert product["Name"] == "Test Product"

        # Non-existent product
        product = get_specific_goods(999)
        assert product is None


def test_get_customer_purchases(test_app):
    with test_app.app_context():
        purchases = get_customer_purchases("johndoe")
        assert purchases is not None
        assert len(purchases) == 1
        assert purchases[0]["product_name"] == "Test Product"


def test_add_to_wishlist(test_app):
    with test_app.app_context():
        # Fetch dynamic ProductID
        product_id = next(item["ProductID"] for item in get_all_items() if item["Name"] == "Test Product")

        # Add item to wishlist
        response = add_to_wishlist("johndoe", product_id)
        assert response == {"message": "Product added to wishlist successfully"}

        # Attempt to add the same item again
        response = add_to_wishlist("johndoe", product_id)
        assert response == {"error": "Product already in wishlist"}

        # Invalid product
        response = add_to_wishlist("johndoe", 999)
        assert response == {"error": "Product not found"}


def test_fetch_wishlist(test_app):
    with test_app.app_context():
        wishlist = fetch_wishlist("johndoe")
        assert wishlist is not None
        assert len(wishlist) == 1
        assert wishlist[0]["product_name"] == "Test Product"


def test_recommend_products(test_app):
    with test_app.app_context():
        # Add more products to test recommendations
        add_item(
            name="Recommended Product",
            category="Electronics",
            price=200.0,
            description="A recommended product.",
            stock=5
        )

        recommendations = recommend_products("johndoe", limit=1)
        assert recommendations is not None
        assert len(recommendations) == 1
        assert recommendations[0]["Name"] == "Apple iPhone 14"
