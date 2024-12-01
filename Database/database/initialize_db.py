import sqlite3
from werkzeug.security import generate_password_hash
import os

def initialize_db(db_path='ecommerce.db'):
    """
    Initialize the database by creating tables and inserting initial data.

    Steps:
        1. Connect to the SQLite database 'ecommerce.db'.
        2. Execute the SQL schema from 'schema.sql' to create necessary tables.
        3. Insert an initial admin user into the Customers table with the following attributes:
           - FullName: 'Admin User'
           - Username: 'admin'
           - Password: Hashed password of 'admin_password'
           - Age: 30
           - Address: '123 Admin St'
           - Gender: 'Male'
           - MaritalStatus: 'Single'
           - Wallet: 0
           - UserRole: 1 (indicating admin role)
        4. Commit the changes and close the database connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)

    admin_user = ('Admin User', 'admin', generate_password_hash('admin_password'), 30, '123 Admin St', 'Male', 'Single', 0, 1)
    cursor.execute('''
        INSERT OR IGNORE INTO Customers 
        (FullName, Username, Password, Age, Address, Gender, MaritalStatus, Wallet, UserRole)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', admin_user)

    sample_items = [
        ('Apple iPhone 14', 'Electronics', 999.99, 'Latest Apple smartphone.', 50),
        ('Samsung Galaxy S23', 'Electronics', 899.99, 'High-end Android smartphone.', 40),
        ('Leather Jacket', 'Clothes', 149.99, 'Stylish leather jacket.', 30),
        ('Wireless Earbuds', 'Accessories', 49.99, 'High-quality wireless earbuds.', 100),
        ('Organic Almonds', 'Food', 19.99, 'Healthy organic almonds.', 200),
        ('Sony WH-1000XM4', 'Electronics', 349.99, 'Noise-cancelling over-ear headphones.', 25),
        ('Dell XPS 13', 'Electronics', 1199.99, 'High-performance laptop.', 15),
        ('Nike Air Max', 'Clothes', 129.99, 'Comfortable running shoes.', 60),
        ('Ray-Ban Sunglasses', 'Accessories', 159.99, 'Stylish sunglasses.', 80),
        ('Organic Quinoa', 'Food', 9.99, 'Healthy organic quinoa.', 150)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO Inventory 
        (Name, Category, Price, Description, Stock)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_items)

    conn.commit()
    conn.close()
