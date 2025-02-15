import uuid
import random
import csv
from datetime import datetime, timedelta

categories = [
    "food",
    "travel",
    "transport",
    "entertainment",
    "utilities",
    "grocery",
    "shopping",
    "electronics",
    "health",
    "miscellaneous",
    "automobile",
    "other",
    "none",
]

descriptions = {
    "food": ["lunch", "dinner", "breakfast", "snack", "restaurant meal"],
    "travel": [
        "bus ticket",
        "flight booking",
        "hotel booking",
        "taxi fare",
        "rental car",
    ],
    "transport": ["gas", "public transport", "toll fees", "maintenance", "car wash"],
    "entertainment": [
        "movie tickets",
        "concert",
        "theater",
        "game night",
        "amusement park",
    ],
    "utilities": [
        "electricity bill",
        "water bill",
        "gas bill",
        "internet bill",
        "phone bill",
    ],
    "grocery": [
        "supermarket shopping",
        "farmers market",
        "bulk food",
        "vegetable purchase",
    ],
    "shopping": ["clothes", "accessories", "gadgets", "books"],
    "electronics": ["phone purchase", "laptop", "tablet", "TV", "headphones"],
    "health": ["medication", "doctor visit", "gym membership", "health supplements"],
    "miscellaneous": ["various items", "unexpected expense", "misc purchase"],
    "automobile": ["car repair", "oil change", "spare parts", "car accessories"],
    "other": ["other expense", "general expense"],
    "none": ["no description"],
}


def generate_random_expense():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 2, 15)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    date_str = random_date.strftime("%Y-%m-%d")

    record_id = uuid.uuid4().hex
    amount = round(random.uniform(9.99, 999.99), 2)
    category = random.choice(categories)
    description = random.choice(descriptions[category])

    return {
        "id": record_id,
        "date": date_str,
        "amount": amount,
        "category": category,
        "description": description,
    }


num_records = 1200
filename = "filtered_expenses.csv"

with open(filename, mode="w", newline="") as csv_file:
    fieldnames = ["id", "date", "amount", "category", "description"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for _ in range(num_records):
        expense_record = generate_random_expense()
        writer.writerow(expense_record)

print(f"Saved {num_records} records to '{filename}'.")
