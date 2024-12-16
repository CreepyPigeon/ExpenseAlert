import sqlite3
import json

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
