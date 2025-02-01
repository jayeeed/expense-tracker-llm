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
    NONE = "none"


@tool("add_expense", response_format="content")
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


@tool("search_expense", response_format="content")
def search_by_fields(
    date: Optional[str] = None,
    amount: Optional[float] = None,
    category: Optional[str] = None,
) -> str:
    """Search expenses by category, amount, or date."""

    query = "SELECT * FROM expenses WHERE "
    conditions = []
    if category:
        conditions.append(f"LOWER(category) = '{category}'")
    if amount:
        conditions.append(f"amount = {amount}")
    if date:
        conditions.append(f"CAST(date AS TEXT) = '{date}'")
    if not conditions:
        return "No search criteria provided."
    query += " AND ".join(conditions)

    print("query:", query)

    return db_query(query)


tools = [create_expense, search_by_fields]
