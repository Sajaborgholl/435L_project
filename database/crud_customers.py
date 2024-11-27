import sqlite3
from connect_db import get_db_connection


# Register a new customer
def register_customer(full_name, username, password, age, address, gender, marital_status):
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
    conn = get_db_connection()
    cursor = conn.cursor()
    customers = cursor.execute('SELECT CustomerID, FullName, Username, Age, Address, Gender, MaritalStatus, Wallet, UserRole FROM Customers').fetchall()
    conn.close()
    return [dict(customer) for customer in customers]


# Get a single customer by username (exclude password)
def get_customer_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    customer = cursor.execute('SELECT CustomerID, FullName, Username, Age, Address, Gender, MaritalStatus, Wallet, UserRole FROM Customers WHERE Username = ?', (username,)).fetchone()
    conn.close()
    return dict(customer) if customer else None


# Charge a customer's wallet
def charge_customer(username, amount):
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
