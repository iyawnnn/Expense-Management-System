import sqlite3
import datetime
import locale
from tabulate import tabulate
import matplotlib.pyplot as plt

# Set locale based on user preferences
locale.setlocale(locale.LC_MONETARY, 'fil_PH.UTF-8')

# Function to validate date input
def validate_date_input(date_string):
    while True:
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
            if date > datetime.datetime.now():  # Check for future dates
                print("Future dates are not allowed for expenses.")
                date_string = input("Enter the date of the expense (YYYY-MM-DD):\n")
            else:
                return date
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")
            date_string = input("Enter the date of the expense (YYYY-MM-DD):\n")

# Function to validate price input
def validate_price_input(price_string):
    while True:
        try:
            price = float(price_string)
            if price >= 0:  # Check for non-negative price
                return price
            else:
                print("Invalid price. Please enter a non-negative number.")
                price_string = input("Enter the price of the expense:\n")
        except ValueError:
            print("Invalid price format. Please enter a valid number.")
            price_string = input("Enter the price of the expense:\n")

# Function to add a new expense
def add_new_expense(cursor, connection):
    print("\nPlease provide the following details for the new expense:")
    date = validate_date_input(input("Enter the date of the expense (YYYY-MM-DD):\n"))
    description = input("\nEnter the description of the expense:\n").upper()
    cursor.execute("SELECT DISTINCT category FROM expenses")
    categories = cursor.fetchall()
    print("\nSelect a category by number:")
    for idx, category in enumerate(categories):
        print(f"{idx + 1}. {category[0]}")
    print(f"{len(categories) + 1}. Create a new category")
    while True:
        try:
            category_choice = int(input())
            if 1 <= category_choice <= len(categories) + 1:
                break
            else:
                print("Invalid choice. Please choose a valid category number.")
        except ValueError:
            print("Invalid input. Please enter a valid category number.")
    if category_choice == len(categories) + 1:
        category = input("\nEnter the new category name:\n").upper()
    else:
        category = categories[category_choice - 1][0]
    price = validate_price_input(input("\nEnter the price of the expense:\n"))
    cursor.execute("INSERT INTO expenses (Date, description, category, price) VALUES (?, ?, ?, ?)",
                   (date.strftime("%Y-%m-%d"), description, category, price))
    connection.commit()  # Inserting expense details into the database

# Function to view all expenses and display a pie chart
def view_all_expenses(cursor):
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    formatted_expenses = []
    for expense in expenses:
        formatted_price = locale.currency(expense[4], grouping=True)
        formatted_expense = [expense[1], expense[2], expense[3], formatted_price]
        formatted_expenses.append(formatted_expense)
    print(tabulate(formatted_expenses, headers=["Date", "Description", "Category", "Price"], tablefmt="grid"))
    display_expenses_pie_chart(cursor)  # Display pie chart for expenses by category

# Function to view monthly expenses by category
def view_monthly_expenses(cursor):
    while True:
        try:
            date_input = input("\nEnter the month and year (MM/YYYY): ")
            month, year = date_input.split('/')
            datetime.datetime.strptime(f"{year}-{month}", "%Y-%m")  # Validate year and month format
            break
        except ValueError:
            print("Invalid input. Please enter a valid month (MM) and year (YYYY) in the format 'MM/YYYY'.")
    cursor.execute("""SELECT Date, description, category, SUM(price) FROM expenses
                    WHERE strftime('%m', Date) = ? AND strftime('%Y', Date) = ?
                    GROUP BY Date, description, category""", (month, year))
    expenses = cursor.fetchall()
    formatted_expenses = []
    for expense in expenses:
        formatted_price = locale.currency(expense[3], grouping=True)
        formatted_expense = [expense[0], expense[1], expense[2], formatted_price]
        formatted_expenses.append(formatted_expense)
    print()
    print(tabulate(formatted_expenses, headers=["Date", "Description", "Category", "Total Price"], tablefmt="grid"))

# Function to calculate total expenses
def total_expenses(cursor):
    cursor.execute("SELECT SUM(price) FROM expenses")
    total = cursor.fetchone()[0]
    return total if total else 0

# Function to calculate average expenses per month
def average_expenses_per_month(cursor):
    cursor.execute("SELECT strftime('%Y-%m', Date) AS month, SUM(price) AS total "
                   "FROM expenses GROUP BY strftime('%Y-%m', Date)")
    monthly_expenses = cursor.fetchall()
    total_months = len(monthly_expenses)
    total = sum(row[1] for row in monthly_expenses)
    return total / total_months if total_months > 0 else 0

# Function to calculate expenses by category
def expenses_by_category(cursor):
    cursor.execute("SELECT category, SUM(price) FROM expenses GROUP BY category")
    category_expenses = cursor.fetchall()
    formatted_category_expenses = []
    for category in category_expenses:
        category_name = category[0]
        category_total = float(category[1])  # Convert the total to float
        formatted_category_expense = [category_name, category_total]
        formatted_category_expenses.append(formatted_category_expense)
    return formatted_category_expenses

# Function for the data analysis menu
def data_analysis_menu(cursor):
    while True:
        print("\nData Analysis Menu:")
        print("1. Total expenses")
        print("2. Average expenses per month")
        print("3. Expenses by category")
        print("4. Back to main menu")
        choice = input()
        if choice == '1':
            total = total_expenses(cursor)
            print(f"\nTotal expenses: {locale.currency(total, grouping=True)}")
        elif choice == '2':
            average = average_expenses_per_month(cursor)
            print(f"\nAverage expenses per month: {locale.currency(average, grouping=True)}")
        elif choice == '3':
            category_expenses = expenses_by_category(cursor)
            print("\nExpenses by category:")
            formatted_expenses = [[cat, locale.currency(total, grouping=True)] for cat, total in category_expenses]
            print(tabulate(formatted_expenses, headers=["Category", "Total Price"], tablefmt="grid"))
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please choose a valid option.")

# Function to display a pie chart for expenses by category
def display_expenses_pie_chart(cursor):
    category_expenses = expenses_by_category(cursor)
    categories = [category[0] for category in category_expenses]
    expenses = [category[1] for category in category_expenses]
    total_expense = sum(expenses)
    percentages = [(expense / total_expense) * 100 for expense in expenses]
    max_index = percentages.index(max(percentages))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    explode = [0.1 if i == max_index else 0 for i in range(len(categories))]
    plt.figure(figsize=(8, 8))
    plt.pie(expenses, labels=categories, autopct=lambda pct: f"{pct:.1f}%", startangle=140,
            colors=colors, explode=explode, shadow=True, wedgeprops={'linewidth': 2, 'edgecolor': 'black'})
    plt.title('Expense Management System', fontname='Arial', fontsize=16, fontweight='bold')
    plt.legend(loc="upper right", labels=['%s: %.1f%%' % (l, s) for l, s in zip(categories, percentages)])
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Function to manage expenses
def manage_expenses():
    conn = sqlite3.connect("expenses.db")
    cur = conn.cursor()
    exit_commands = ['n', 'no', 'exit', 'quit']  # Adding more exit commands for flexibility
    while True:
        print("\nSelect an option:")
        print("1. Enter a new expense")
        print("2. View all expenses")
        print("3. View monthly expenses by category")
        print("4. Data Analysis")
        print("5. Exit")
        choice = input()
        if choice == '1':
            add_new_expense(cur, conn)
        elif choice == '2':
            view_all_expenses(cur)
        elif choice == '3':
            view_monthly_expenses(cur)
        elif choice == '4':
            data_analysis_menu(cur)
        elif choice == '5':
            print("Exiting the expense manager. Thank you!")
            break
        else:
            print("Invalid choice. Please choose a valid option.")
        while True:
            response = input("\nWould you like to do something else? (Type 'exit' or 'n' to quit, or press Enter to continue)\n")
            if response.lower() in exit_commands or response == '':
                break
            else:
                print("Invalid input. Please enter 'exit', 'n', or press Enter to continue.")
        if response.lower() in exit_commands:
            print("\nExiting the expense manager. Thank you!")
            break
    conn.close()  # Closing the database connection

if __name__ == "__main__":
    print("Welcome to the Expense Manager!")
    manage_expenses()
