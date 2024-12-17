import sqlite3
import logging

DB_PATH = "ExpenseAlert/expenses.db"

def categorize_miscellaneous_expenses():
    """Categorize expenses initially put in the miscellaneous category"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, invoice_id, date, amount
            FROM invoices
            WHERE category = "Miscellaneous"
        ''')
        miscellaneous_expenses = cursor.fetchall()

        if not miscellaneous_expenses:
            print("Nothing in the Miscellaneous category")
            return

        print("\nMiscellaneous expenses:")
        for index, (expense_id, invoice_id, date, amount) in enumerate(miscellaneous_expenses, start=1):
            print(f"{index}. ID: {invoice_id}, Date: {date}, Amount: {amount:.2f}")

        choice = int(input("\nSelect the index of the expense you want to recategorize (press 0 to exit): "))
        if choice == 0:
            return

        selected_expense = miscellaneous_expenses[choice - 1]
        expense_id = selected_expense[0]

        new_category = input("Type the new category: ")

        cursor.execute('''
            UPDATE invoices
            SET category = ?
            WHERE id = ?
        ''', (new_category, expense_id))
        conn.commit()
        print(f"Category successfully updated for expense id = {expense_id}")
        logging.info(f"Category successfully updated for expense id = {expense_id}")
    except Exception as e:
        print(f"Error changing category for expense id = {expense_id}: {e}")
        logging.error(f"Error changing category for expense id = {expense_id}: {e}")
    finally:
        conn.close()


def initialize_database():
    """Creates the tables in the database if they don't already exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                budget_limit REAL NOT NULL
            )
        ''')

        conn.commit()
        print("Database initialized successfully.")
        logging.info("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        logging.error(f"Error initializing database: {e}", exc_info=True)
    finally:
        conn.close()

def sync_budget_limits_to_db(limits):
    """Loads budget limits from the JSON file and updates the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for category, limit in limits.items():
            cursor.execute('''
                INSERT INTO categories (category, budget_limit)
                VALUES (?, ?)
                ON CONFLICT(category) DO UPDATE SET budget_limit = excluded.budget_limit
            ''', (category, limit))

        conn.commit()
        logging.info("Budget limits synchronized")
        print("Budget limits synchronized.")
    except Exception as e:
        logging.error(f"Error syncing budget limits: {e}", exc_info=True)
        print(f"Error syncing budget limits: {e}")
    finally:
        conn.close()

def save_invoice_to_db(invoice_data):
    """Saves an invoice to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO invoices (invoice_id, date, amount, category)
            VALUES (?, ?, ?, ?)
        ''', (invoice_data['id'], invoice_data['date'], invoice_data['amount'], invoice_data['category']))

        conn.commit()
        logging.info(f"Invoice {invoice_data['id']} saved successfully in category '{invoice_data['category']}'.")
        print(f"Invoice {invoice_data['id']} saved successfully.")
    except Exception as e:
        print(f"Error saving invoice{invoice_data['id']}: {e}")
        logging.error(f"Error saving invoice {invoice_data['id']}: {e}", exc_info=True)
    finally:
        conn.close()


def check_budget_from_db(category):
    """Checks if the total spending for a category exceeds the budget limit."""
    try:
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM(amount) 
            FROM invoices 
            WHERE category = ?
        ''', (category,))
        total_spent = cursor.fetchone()[0]

        cursor.execute('''
            SELECT budget_limit 
            FROM categories 
            WHERE category = ?
        ''', (category,))
        budget_limit = cursor.fetchone()[0]
        if total_spent > budget_limit:
            alert_message = (
                f"ALERT: Total spending in category '{category}' "
                f"({total_spent:.2f}) exceeds the budget limit of {budget_limit:.2f}."
            )
            logging.warning(alert_message)
            return alert_message

        return None
    except Exception as e:
        print(f"Error checking budget: {e}")
        logging.error(f"Error checking budget: {e}", exc_info=True)
    finally:
        conn.close()
