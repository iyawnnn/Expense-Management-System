import sqlite3
import datetime

def add_new_expense(cursor, connection):
    date = input("Enter the date of the expense (YYYY-MM-DD):\n")
    description = input("Enter the description of the expense:\n")

    cursor.execute("SELECT DISTINCT category FROM expenses")
    categories = cursor.fetchall()

    print("Select a category by number: ")
    for idx, category in enumerate(categories):
        print(f"{idx + 1}. {category[0]}")
    print(f"{len(categories) + 1}. Create a new category")

    category_choice = int(input())
    if category_choice == len(categories) + 1:
        category = input("Enter the new category name:\n")
    else:
        category = categories[category_choice - 1][0]

    price = float(input("Enter the price of the expense:\n"))  # Convert input to float

    cursor.execute("INSERT INTO expenses (Date, description, category, price) VALUES (?, ?, ?, ?)",
                   (date, description, category, price))
    connection.commit()

def view_expense_summary(cursor):
    print("Select an option:\n")
    print("1. View all expenses")
    print("2. View monthly expenses by category")
    view_choice = int(input())
    if view_choice == 1:
        cursor.execute("SELECT * FROM expenses")
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)
    elif view_choice == 2:
        month = input("Enter the month (MM):\n")
        year = input("Enter the year (YYYY):\n")
        cursor.execute("""SELECT category, SUM(price) FROM expenses
                        WHERE strftime('%m', Date) = ? AND strftime('%Y', Date) = ?
                        GROUP BY category""", (month, year))
        expenses = cursor.fetchall()
        for expense in expenses:
            print(f"Category: {expense[0]}, Total: {expense[1]}")

def manage_expenses():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()

    while True:
        print("Select an option:")
        print("1. Enter a new expense")
        print("2. View expenses summary")
        print("3. Exit")

        choice = int(input())

        if choice == 1:
            add_new_expense(cur, conn)
        elif choice == 2:
            view_expense_summary(cur)
        elif choice == 3:
            break
        else:
            print("Invalid choice. Please choose a valid option.")

        repeat = input("Would you like to do something else (y/n)?\n")
        if repeat.lower() != "y":
            break

    conn.close()

if __name__ == "__main__":
    manage_expenses()
