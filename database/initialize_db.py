import sqlite3
from werkzeug.security import generate_password_hash

def initialize_db():
    # Connect to the database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Open and execute the SQL schema file
    with open('schema.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)

    # Insert an admin user
    admin_user = ('Admin User', 'admin', generate_password_hash('admin_password'), 30, '123 Admin St', 'Male', 'Single', 0, 1)
    cursor.execute('''
        INSERT INTO Customers (FullName, Username, Password, Age, Address, Gender, MaritalStatus, Wallet, Role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', admin_user)

    # Commit changes and close the connection
    conn.commit()
    conn.close()



if __name__ == "__main__":
    initialize_db()
