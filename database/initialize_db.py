import sqlite3


def initialize_db():
    # Connect to the database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    # Open and execute the SQL schema file
    with open('schema.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
