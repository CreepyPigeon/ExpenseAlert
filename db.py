import sqlite3

DB_PATH = "ExpenseAlert/expenses.db"

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
    except Exception as e:
        print(f"Error initializing database: {e}")
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
        print("Budget limits synchronized.")
    except Exception as e:
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
        print(f"Invoice {invoice_data['id']} saved successfully.")
    except Exception as e:
        print(f"Error saving invoice{invoice_data['id']}: {e}")
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
            return alert_message
        return None
    except Exception as e:
        print(f"Error checking budget: {e}")
    finally:
        conn.close()
