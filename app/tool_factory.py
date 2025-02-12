from datetime import datetime
from enum import Enum
from typing import Optional
from langchain_core.tools import tool
from app.db_utils import *
import os

db_uri = os.getenv("POSTGRES_URL")


class Category(Enum):
    FOOD = "food"
    TRAVEL = "travel"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    GROCERY = "grocery"
    SHOPPING = "shopping"
    ELECTRONICS = "electronics"
    HEALTH = "health"
    MISCELLANEOUS = "miscellaneous"
    AUTOMOBILE = "automobile"
    OTHER = "other"
    NONE = "none"


@tool
def create_expense(
    id: str,
    date: str,
    amount: float,
    category: Category,
    description: str,
) -> dict:
    """Tool for representing an expense."""

    return {
        "id": id,
        "date": date,
        "amount": amount,
        "category": category.value,
        "description": description,
    }


@tool
def search_by_fields(
    date: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    amount: Optional[float] = None,
    category: Optional[str] = None,
    operation: Optional[str] = "*",
) -> str:
    """Search expenses by category, amount, or date and perform SQL operations (e.g., sum(amount), avg(amount), min(amount), max(amount)) on the result set in PostgreSQL."""

    query = f"SELECT {operation} FROM expenses WHERE "

    conditions = []

    if date:
        conditions.append(f"date = '{date}'")
    if from_date and to_date:
        conditions.append(f"date::DATE BETWEEN '{from_date}' AND '{to_date}'")
    if category:
        conditions.append(f"LOWER(category) = '{category}'")
    if amount:
        conditions.append(f"amount = {amount} ORDER BY date desc")

    if not conditions:
        return "No search criteria provided."
    query += " AND ".join(conditions)

    print("query:", query)
    return db_query(query)


@tool
def sum_avg_min_max(category: str, operation: str) -> str:
    """Sum, average, min, or max expenses by category."""

    query = (
        f"SELECT {operation}(amount) FROM expenses WHERE LOWER(category) = '{category}'"
    )

    print("query:", query)
    return db_query(query)


@tool
def greetings() -> str:
    """Greet the user based on the current time of day and invite them to create or find expenses."""

    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return greeting + ", Boss! You can create or find expenses."


@tool
def unknown() -> str:
    """Handle unknown intents."""

    return "Could not determine intent. Please refine your input."


tools = [
    create_expense,
    search_by_fields,
    # sum_avg_min_max,
    greetings,
    unknown,
]
