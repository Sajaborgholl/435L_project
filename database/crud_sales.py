from connect_db import get_db_connection
from crud_inventory import get_product_by_id, deduct_item
from crud_customers import get_customer_by_username, deduct_money
from datetime import datetime
import json

def record_sale(customer_username, product_id, quantity):
    """
    Records a sale transaction if the purchase is valid, and adds the purchase in the purchase history of the customer.

    Args:
        customer_username (str): The username of the customer.
        product_id (int): The ID of the product being purchased.
        quantity (int): The quantity of the product to purchase.

    Returns:
        dict: A dictionary containing a success or error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch customer and product details
    customer = get_customer_by_username(customer_username)
    product = get_product_by_id(product_id)

    if not customer:
        return {"error": "Customer not found"}
    if not product:
        return {"error": "Product not found"}

    total_price = product["Price"] * quantity

    # Check wallet balance and stock availability
    if customer["Wallet"] < total_price:
        return {"error": "Insufficient wallet balance"}
    if product["Stock"] < quantity:
        return {"error": "Insufficient stock"}

    # Deduct money and stock

    deduct_money(customer_username, total_price)
    deduct_item(product_id, quantity)

    # Record the sale
    cursor.execute('''
        INSERT INTO Sales (CustomerUsername, ProductID, Quantity, TotalPrice)
        VALUES (?, ?, ?, ?)
    ''', (customer_username, product_id, quantity, total_price))

    cursor.execute('''
        SELECT PurchaseHistory FROM HistoricalPurchases WHERE CustomerUsername = ?
    ''', (customer_username,))
    history = cursor.fetchone()

    new_purchase = {
        "product_id": product["ProductID"],
        "product_name": product["Name"],
        "quantity": quantity,
        "total_price": total_price
    }

    if history:
        # Update existing history
        purchase_history = json.loads(history[0])
        purchase_history.append(new_purchase)
        cursor.execute('''
            UPDATE HistoricalPurchases SET PurchaseHistory = ? WHERE CustomerUsername = ?
        ''', (json.dumps(purchase_history), customer_username))
    else:
        # Create new history
        purchase_history = [new_purchase]
        cursor.execute('''
            INSERT INTO HistoricalPurchases (CustomerUsername, PurchaseHistory)
            VALUES (?, ?)
        ''', (customer_username, json.dumps(purchase_history)))

    conn.commit()
    conn.close()

    return {"message": "Sale recorded successfully"}

def get_goods():
    """
    Fetch all goods records with product name and price from the inventory.

    Returns:
        list: A list of dictionaries with all the goods records including product name and price.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Name, Price
        FROM Inventory
    ''')
    goods = cursor.fetchall()
    goods = [dict(good) for good in goods]
    conn.close()
    return goods

def fetch_sales():
    """
    Fetch all sales records.

    Returns:
        list: A list of dictionaries with all the sales records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Sales")
    sales = cursor.fetchall()
    sales = [dict(sale) for sale in sales]
    conn.close()
    return sales


def get_specific_goods(product_id):
    """
    Fetch a specific product from the inventory.

    Args:
        product_id (int): The ID of the product to fetch.

    Returns:
        dict: A dictionary containing the product details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Name, Price
        FROM Inventory
        WHERE ProductID = ?
    ''', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return dict(product) if product else None

def get_customer_purchases(username):
    """
    Fetch the purchase history of a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        list: A list of dictionaries containing the purchase history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT PurchaseHistory
        FROM HistoricalPurchases
        WHERE CustomerUsername = ?
    ''', (username,))
    history = cursor.fetchone()
    conn.close()
    return json.loads(history[0]) if history else None

def add_to_wishlist(username, product_id):
    """
    Add a product to the wishlist of a specific customer.

    Args:
        username (str): The username of the customer.
        product_id (int): The ID of the product to add to the wishlist.

    Returns:
        dict: A dictionary containing a success or error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT List FROM Wishlist WHERE CustomerUsername = ?
    ''', (username,))
    wishlist = cursor.fetchone()

    product = get_product_by_id(product_id)
    if not product:
        conn.close()
        return {"error": "Product not found"}
    
    product = {
        "product_id": product["ProductID"],
        "product_name": product["Name"],
        "price": product["Price"]
    }

    if wishlist:
        wishlist = json.loads(wishlist[0])
        if any(item["product_id"] == product_id for item in wishlist):
            conn.close()
            return {"error": "Product already in wishlist"}
        wishlist.append(product)
        cursor.execute('''
            UPDATE Wishlist SET List = ? WHERE CustomerUsername = ?
        ''', (json.dumps(wishlist), username))
    else:
        wishlist = [product]
        cursor.execute('''
            INSERT INTO Wishlist (CustomerUsername, List)
            VALUES (?, ?)
        ''', (username, json.dumps(wishlist)))

    conn.commit()
    conn.close()

    return {"message": "Product added to wishlist successfully"}

def fetch_wishlist(username):
    """
    Fetch the wishlist of a specific customer.

    Args:
        username (str): The username of the customer.

    Returns:
        list: A list of dictionaries containing the wishlist items.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT List
        FROM Wishlist
        WHERE CustomerUsername = ?
    ''', (username,))
    wishlist = cursor.fetchone()
    conn.close()
    return json.loads(wishlist[0]) if wishlist else None