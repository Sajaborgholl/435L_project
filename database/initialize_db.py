import sqlite3
from werkzeug.security import generate_password_hash
import os

def initialize_db():
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_dir, 'schema.sql')
    # Connect to the database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    
    # Open and execute the SQL schema file
    with open(schema_path, 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)

    # Insert an admin user
    admin_user = ('Admin User', 'admin', generate_password_hash('admin_password'), 30, '123 Admin St', 'Male', 'Single', 0, 1)
    cursor.execute('''
        INSERT OR IGNORE INTO Customers (FullName, Username, Password, Age, Address, Gender, MaritalStatus, Wallet, UserRole)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', admin_user)

    # Commit changes and close the connection
    conn.commit()
    conn.close()



if __name__ == "__main__":
    initialize_db()
