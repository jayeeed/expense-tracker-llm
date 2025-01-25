import psycopg2
import os

db_uri = os.getenv("POSTGRES_URL")


def init_db():
    conn = psycopg2.connect(db_uri)
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
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Connected to:", db_version)

    conn.commit()
    return conn


conn = init_db()


def save_to_db(expense_data):
    with psycopg2.connect(db_uri) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (id, date, amount, category, description)
            VALUES (%s, %s, %s, %s, %s)
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
