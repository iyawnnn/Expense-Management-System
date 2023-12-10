import sqlite3

def create_expenses_table():
    # Context manager (using 'with' statement) to ensure proper closing of the connection
    with sqlite3.connect("expenses.db") as conn:
        cur = conn.cursor()

        # Create expenses table if it doesn't exist
        cur.execute("""CREATE TABLE IF NOT EXISTS expenses
                    (number INTEGER PRIMARY KEY,
                    Date DATE,
                    description TEXT,
                    category TEXT,
                    price REAL)""")
        
        # Commit changes and close the connection
        conn.commit()

# Calling the function to create the expenses table
create_expenses_table()
