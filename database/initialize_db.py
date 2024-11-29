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
    
    conn.commit()
    conn.close()
