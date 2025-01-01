import sqlite3

# Initialize SQLite database
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id TEXT PRIMARY KEY,
        date TEXT,
        amount REAL,
        category TEXT,
        description TEXT
    )
"""
)
conn.commit()


def save_to_db(expense_data):
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (id, date, amount, category, description)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                expense_data["id"],
                expense_data["date"],
                expense_data["amount"],
                expense_data["category"],
                expense_data["description"],
            ),
        )
        conn.commit()


def get_from_db(search_query):
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM expenses
            WHERE date LIKE ? OR amount LIKE ? OR category LIKE ? OR description LIKE ?
        """,
            (
                f"%{search_query}%",
                f"%{search_query}%",
                f"%{search_query}%",
                f"%{search_query}%",
            ),
        )
        return cursor.fetchall()
