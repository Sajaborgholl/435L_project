import sqlite3

def get_db_connection():
    """
    Establishes a connection to the SQLite database 'ecommerce.db' and sets the row factory to sqlite3.Row.

    Returns:
        sqlite3.Connection: A connection object to the 'ecommerce.db' database.
    """
    conn = sqlite3.connect('ecommerce.db')
    conn.row_factory = sqlite3.Row
    return conn