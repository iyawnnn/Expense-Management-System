import sqlite3
import datetime
import locale
from tabulate import tabulate

def add_new_expense(cursor, connection):
    while True:
        date = input("\nEnter the date of the expense (YYYY-MM-DD):\n")
        if not validate_date_format(date):
            print("Invalid date format. Please use YYYY-MM-DD format.")  # Validate date format
            continue
        else:
            break

    description = input("\nEnter the description of the expense:\n").upper()

    cursor.execute("SELECT DISTINCT category FROM expenses")
    categories = cursor.fetchall()

    print("\nSelect a category by number:")
    for idx, category in enumerate(categories):
        print(f"{idx + 1}. {category[0]}")
    print(f"{len(categories) + 1}. Create a new category")

    while True:
        category_choice = input()
        if not category_choice.isdigit() or not (1 <= int(category_choice) <= len(categories) + 1):
            print("Invalid choice. Please choose a valid category number.")
            continue
        else:
            category_choice = int(category_choice)
            break

    if category_choice == len(categories) + 1:
        category = input("\nEnter the new category name:\n").upper() 
    else:
        category = categories[category_choice - 1][0]

    while True:
        price = input("\nEnter the price of the expense:\n")
        if not validate_price(price):
            print("Invalid price format. Please enter a valid number.")
            continue
        else:
            price = float(price)
            break

    cursor.execute("INSERT INTO expenses (Date, description, category, price) VALUES (?, ?, ?, ?)",
                   (date, description, category, price))
    connection.commit()  # Inserting expense details into the database

def view_expense_summary(cursor):
    locale.setlocale(locale.LC_MONETARY, 'en_PH.UTF-8')  # Setting PHP currency locale
    print("\nSelect an option:")
    print("1. View all expenses")
    print("2. View monthly expenses by category")
    view_choice = input()  
    if view_choice == '1':
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()
        formatted_expenses = []
        for expense in expenses:
            formatted_price = locale.currency(expense[4], grouping=True)
            formatted_expense = [expense[1], expense[2], expense[3], formatted_price]
            formatted_expenses.append(formatted_expense)
        print()
        print(tabulate(formatted_expenses, headers=["Date", "Description", "Category", "Price"], tablefmt="grid"))
        # Displaying all expenses in tabular format
    elif view_choice == '2':
        month = input("\nEnter the month (MM):\n")
        year = input("\nEnter the year (YYYY):\n")
        cursor.execute("""SELECT category, SUM(price) FROM expenses
                        WHERE strftime('%m', Date) = ? AND strftime('%Y', Date) = ?
                        GROUP BY category""", (month, year))
        expenses = cursor.fetchall()
        formatted_expenses = []
        for expense in expenses:
            formatted_price = locale.currency(expense[1], grouping=True)
            formatted_expense = [expense[0], formatted_price]
            formatted_expenses.append(formatted_expense)
        print()
        print(tabulate(formatted_expenses, headers=["Category", "Total Price"], tablefmt="grid"))
        # Displaying monthly expenses by category in tabular format

def validate_date_format(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")  # Validate date format
        return True
    except ValueError:
        return False

def validate_price(price):
    try:
        float(price)  # Validate price format
        return True
    except ValueError:
        return False

def manage_expenses():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    while True:
        print("\nSelect an option:")
        print("1. Enter a new expense")
        print("2. View expenses summary")
        print("3. Exit")
        
        choice = input()  
        
        if choice == '1':
            add_new_expense(cur, conn)
        elif choice == '2':
            view_expense_summary(cur)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

        repeat = input("\nWould you like to do something else (y/n)?\n")
        if repeat.lower() != "y":
            break

    conn.close()  # Closing the database connection

if __name__ == "__main__":
    manage_expenses()
