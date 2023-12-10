import sqlite3

def create_expenses_table():
    with sqlite3.connect("expenses.db") as conn:
        cur = conn.cursor()

        # Create expenses table if it doesn't exist
        cur.execute("""CREATE TABLE IF NOT EXISTS expenses
                    (number INTEGER PRIMARY KEY,
                    Date DATE,
                    description TEXT,
                    category TEXT,
                    price REAL)""")
        
        
        conn.commit()


create_expenses_table()
