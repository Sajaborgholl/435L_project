import sqlite3
from connect_db import get_db_connection

def get_all_items():
    """
    Retrieve all items from the inventory.

    Returns:
        list: A list of dictionaries containing item details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Inventory')
    items = cursor.fetchall()
    conn.close()
    item_list = [dict(item) for item in items]
    return item_list

def add_item(name, category, price, description, stock):
    """
    Add a new item to the inventory, or update stock if item with same name and price exists.

    Args:
        name (str): The name of the item.
        category (str): The category of the item (e.g., food, clothes, accessories, electronics).
        price (float): The price of a single item.
        description (str): A brief description of the item.
        stock (int): The number of items available in stock.

    Returns:
        dict: A dictionary with a success message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Inventory WHERE Name = ? AND Price = ?', (name, price))
    existing_item = cursor.fetchone()

    if existing_item:
        # If item exists, update the stock
        cursor.execute(
            'UPDATE Inventory SET Stock = Stock + ? WHERE ProductID = ?',
            (stock, existing_item['ProductID'])
        )
        conn.commit()
        conn.close()
        return {"message": "Item stock updated successfully"}
    else:
        cursor.execute('''
            INSERT INTO Inventory (Name, Category, Price, Description, Stock)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category, price, description, stock))
        conn.commit()
        conn.close()
    return {"message": "Item added successfully"}

def deduct_item(item_id, count):
    """
    Deduct stock for a specific item in the inventory.

    Args:
        item_id (int): The ID of the item to be deducted.
        count (int): The number of items to deduct from stock.

    Returns:
        dict: A dictionary with a success message or an error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT Stock FROM Inventory WHERE ProductID = ?', (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return {"error": "Item not found"}

    new_stock = item["Stock"] - count
    if new_stock < 0:
        conn.close()
        return {"error": "Insufficient stock"}

    cursor.execute('UPDATE Inventory SET Stock = ? WHERE ProductID = ?', (new_stock, item_id))
    conn.commit()
    conn.close()
    return {"message": "Item stock updated successfully"}

def update_item(item_id, **fields):
    """
    Update the details of a specific item in the inventory.

    Args:
        item_id (int): The ID of the item to update.
        **fields: Key-value pairs of fields to update (e.g., name='new name', price=99.99).

    Returns:
        dict: A dictionary with a success message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    updates = ', '.join([f'{key} = ?' for key in fields])
    values = list(fields.values()) + [item_id]
    query = f'UPDATE Inventory SET {updates} WHERE ProductID = ?'

    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return {"message": "Item updated successfully"}


def delete_item(item_id):
    """
    Delete a specific item from the inventory.

    Args:
        item_id (int): The ID of the item to delete.

    Returns:
        dict: A dictionary with a success message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Inventory WHERE ProductID = ?', (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted successfully"}

