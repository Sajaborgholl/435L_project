import sqlite3
from connect_db import get_db_connection


# Register a new customer
def register_customer(full_name, username, password, age, address, gender, marital_status):
    """
    Registers a new customer.

    Args:
        full_name (str): Full name of the customer.
        username (str): Unique username for the customer.
        password (str): Password for the customer.
        age (int): Age of the customer.
        address (str): Address of the customer.
        gender (str): Gender of the customer.
        marital_status (str): Marital status of the customer.

    Returns:
        dict: 
            - "message" (str): Success message if registration is successful.
            - "error" (str): Error message if the username already exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Customers (FullName, Username, Password, Age, Address, Gender, MaritalStatus, Wallet, UserRole)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0)
        ''', (full_name, username, password, age, address, gender, marital_status))
        conn.commit()
        return {"message": "Customer registered successfully"}
    except sqlite3.IntegrityError:
        return {"error": "Username already taken"}
    finally:
        conn.close()


# Delete a customer by username
def delete_customer(username):
    """
    Deletes a customer from the database by their username.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        dict: A dictionary containing:
            - "message" (str): Success message if deletion is successful.
            - "error" (str): Error message if the customer does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT * FROM Customers WHERE Username = ?', (username,)).fetchone()
    if not customer:
        conn.close()
        return {"error": "Customer not found"}
    
    cursor.execute('DELETE FROM Customers WHERE Username = ?', (username,))
    conn.commit()
    conn.close()
    return {"message": "Customer deleted successfully"}


# Update customer information
def update_customer(username, **kwargs):
    """
    Updates information for an existing customer.

    Args:
        username (str): The username of the customer to update.
        **kwargs: Key-value pairs representing the fields to update.

    Returns:
        dict: A dictionary containing:
            - "message" (str): Success message if the update is successful.
            - "error" (str): Error message if the customer does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT * FROM Customers WHERE Username = ?', (username,)).fetchone()
    if not customer:
        conn.close()
        return {"error": "Customer not found"}
    
    fields = ', '.join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values())
    values.append(username)
    cursor.execute(f'UPDATE Customers SET {fields} WHERE Username = ?', values)
    conn.commit()
    conn.close()
    return {"message": "Customer updated successfully"}


# Get all customers (exclude passwords)
def get_all_customers():
    """
    Retrieves all customers from the database, excluding passwords.

    Returns:
        list: A list of dictionaries, each containing customer details:
            - CustomerID
            - FullName
            - Username
            - Age
            - Address
            - Gender
            - MaritalStatus
            - Wallet
            - UserRole
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customers = cursor.execute('SELECT CustomerID, FullName, Username, Age, Address, Gender, MaritalStatus, Wallet, UserRole FROM Customers').fetchall()
    conn.close()
    return [dict(customer) for customer in customers]


# Get a single customer by username (exclude password)
def get_customer_by_username(username):
    """
    Retrieves a single customer's details by their username, excluding the password.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        dict: A dictionary containing customer details or None if the customer does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT CustomerID, FullName, Username, Age, Address, Gender, MaritalStatus, Wallet, UserRole FROM Customers WHERE Username = ?', (username,)).fetchone()
    conn.close()
    return dict(customer) if customer else None


# Charge a customer's wallet
def charge_customer(username, amount):
    """
    Charges a customer's wallet by adding a specified amount.

    Args:
        username (str): The username of the customer to charge.
        amount (float): The amount to add to the wallet.

    Returns:
        dict: A dictionary containing:
            - "message" (str): Success message if the wallet is charged successfully.
            - "error" (str): Error message if the customer does not exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT Wallet FROM Customers WHERE Username = ?', (username,)).fetchone()
    if not customer:
        conn.close()
        return {"error": "Customer not found"}

    cursor.execute('UPDATE Customers SET Wallet = Wallet + ? WHERE Username = ?', (amount, username))
    conn.commit()
    conn.close()
    return {"message": "Customer account charged successfully"}


# Deduct money from a customer's wallet
def deduct_money(username, amount):
    """
    Deducts a specified amount from a customer's wallet.

    Args:
        username (str): The username of the customer.
        amount (float): The amount to deduct from the wallet.

    Returns:
        dict: A dictionary containing:
            - "message" (str): Success message if the amount is deducted successfully.
            - "error" (str): Error message if the customer does not exist or if there are insufficient funds.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT Wallet FROM Customers WHERE Username = ?', (username,)).fetchone()
    if not customer:
        conn.close()
        return {"error": "Customer not found"}

    if customer['Wallet'] < amount:
        conn.close()
        return {"error": "Insufficient wallet balance"}

    cursor.execute('UPDATE Customers SET Wallet = Wallet - ? WHERE Username = ?', (amount, username))
    conn.commit()
    conn.close()
    return {"message": "Money deducted from wallet successfully"}
