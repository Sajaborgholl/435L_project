import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crud_inventory import (
    get_all_items,
    get_product_by_id,
    add_item,
    deduct_item,
    update_item,
    delete_item
)

def test_get_all_items(test_app):
    with test_app.app_context():
        items = get_all_items()
        assert len(items) == 10  # Based on the initial data in initialize_db
        item_names = [item['Name'] for item in items]
        assert "Apple iPhone 14" in item_names
        assert "Organic Quinoa" in item_names


def test_get_product_by_id(test_app):
    with test_app.app_context():
        # Retrieve an existing item
        item = get_product_by_id(1)  # Assuming ProductID starts at 1
        assert item is not None
        assert item["Name"] == "Apple iPhone 14"

        # Try to retrieve a non-existent item
        item = get_product_by_id(999)  # Assuming 999 is not a valid ProductID
        assert item is None


def test_add_item(test_app):
    with test_app.app_context():
        # Add a new item
        response = add_item(
            name="Google Pixel 7",
            category="Electronics",
            price=799.99,
            description="High-end Google smartphone.",
            stock=25
        )
        assert response == {"message": "Item added successfully"}

        # Verify the item was added
        items = get_all_items()
        item_names = [item['Name'] for item in items]
        assert "Google Pixel 7" in item_names

        # Add stock to an existing item
        response = add_item(
            name="Apple iPhone 14",
            category="Electronics",
            price=999.99,
            description="Latest Apple smartphone.",
            stock=10
        )
        assert response == {"message": "Item stock updated successfully"}

        # Verify the stock was updated
        item = get_product_by_id(1)  # Assuming ProductID for "Apple iPhone 14" is 1
        assert item["Stock"] == 60  # Initial stock (50) + 10


def test_deduct_item(test_app):
    with test_app.app_context():
        # Deduct stock for an existing item
        response = deduct_item(1, 5)  # Assuming ProductID for "Apple iPhone 14" is 1
        assert response == {"message": "Item stock updated successfully"}

        # Verify the stock was updated
        item = get_product_by_id(1)
        assert item["Stock"] == 55  # Stock after deduction

        # Try to deduct more stock than available
        response = deduct_item(1, 100)
        assert response == {"error": "Insufficient stock"}


def test_update_item(test_app):
    with test_app.app_context():
        # Update item details
        response = update_item(1, Name="Apple iPhone 14 Pro", Price=1099.99)
        assert response == {"message": "Item updated successfully"}

        # Verify the updates
        item = get_product_by_id(1)
        assert item["Name"] == "Apple iPhone 14 Pro"
        assert item["Price"] == 1099.99


def test_delete_item(test_app):
    with test_app.app_context():
        # Delete an existing item
        response = delete_item(1)  # Assuming ProductID for "Apple iPhone 14 Pro" is 1
        assert response == {"message": "Item deleted successfully"}

        # Verify the item was deleted
        item = get_product_by_id(1)
        assert item is None

        # Try to delete a non-existent item
        response = delete_item(999)
        assert response == {"message": "Item deleted successfully"}
