import psycopg2
import os
import csv

db_uri = os.getenv("POSTGRES_URL")
if not db_uri:
    raise ValueError("POSTGRES_URL environment variable is not set")

csv_file_path = "filtered_expenses.csv"


def ingest_data(csv_file_path):
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file '{csv_file_path}' not found.")

    try:
        with psycopg2.connect(db_uri) as conn:
            with conn.cursor() as cursor:
                with open(csv_file_path, mode="r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        cursor.execute(
                            """
                            INSERT INTO expenses (id, date, amount, category, description)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                row["id"].strip().lower(),
                                row["date"].strip(),
                                float(
                                    row["amount"]
                                ),  # Ensure amount is stored as a float
                                row["category"].strip().lower(),
                                row["description"].strip().lower(),
                            ),
                        )
            conn.commit()
        print("Data ingestion completed successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")


ingest_data(csv_file_path)
