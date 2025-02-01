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


@tool("create_expense", response_format="content")
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


@tool("search_by_fields", response_format="content")
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


@tool("sum_expense", response_format="content")
def sum_expense(category: str) -> str:
    """Sum expenses by category."""

    query = f"SELECT SUM(amount) FROM expenses WHERE LOWER(category) = '{category}'"

    return db_query(query)


@tool("min_max_expense", response_format="content")
def min_max_expense(category: str) -> str:
    """Return min and max expenses by category."""

    query = f"SELECT MIN(amount), MAX(amount) FROM expenses WHERE LOWER(category) = '{category}'"

    return db_query(query)


@tool("monthly_expense_summary", response_format="content")
def monthly_expense_summary(year: int, month: int) -> dict:
    """Get a summary of total expenses per category for a given month."""

    query = f"""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE EXTRACT(YEAR FROM date) = {year} AND EXTRACT(MONTH FROM date) = {month}
        GROUP BY category
    """

    return db_query(query)


@tool("average_expense", response_format="content")
def average_expense(category: Optional[str] = None) -> str:
    """Get the average expense amount per category or overall."""

    query = "SELECT category, AVG(amount) FROM expenses"

    if category:
        query += f" WHERE LOWER(category) = '{category}'"

    query += " GROUP BY category"

    return db_query(query)


@tool("expense_anomalies", response_format="content")
def expense_anomalies(threshold: float = 2.0) -> dict:
    """
    Identify expense anomalies where an expense is significantly higher than the category average.
    `threshold` determines how many times above the average an expense should be flagged.
    """

    query = f"""
        SELECT e.id, e.date, e.amount, e.category, e.description
        FROM expenses e
        JOIN (
            SELECT category, AVG(amount) AS avg_amount
            FROM expenses
            GROUP BY category
        ) a ON e.category = a.category
        WHERE e.amount > (a.avg_amount * {threshold})
    """

    return db_query(query)


@tool("recurring_expenses", response_format="content")
def recurring_expenses(min_count: int = 3) -> dict:
    """
    Detect recurring expenses that appear at least `min_count` times.
    """

    query = f"""
        SELECT description, category, COUNT(*) as occurrences, SUM(amount) as total_spent
        FROM expenses
        GROUP BY description, category
        HAVING COUNT(*) >= {min_count}
        ORDER BY occurrences DESC
    """

    return db_query(query)


@tool("check_budget", response_format="content")
def check_budget(category: str, budget_limit: float) -> str:
    """Check if expenses in a category exceed a given budget limit."""

    query = f"""
        SELECT SUM(amount) FROM expenses WHERE LOWER(category) = '{category}'
    """

    total_spent = db_query(query)

    if total_spent and float(total_spent) > budget_limit:
        return f"Warning: You've exceeded your budget for {category}. Spent: {total_spent}, Limit: {budget_limit}"
    else:
        return f"You're within budget for {category}. Spent: {total_spent}, Limit: {budget_limit}"


@tool("unknown", response_format="content")
def unknown() -> str:
    """Handle unknown intents."""

    return "Could not determine intent. Please refine your input."


tools = [
    create_expense,
    search_by_fields,
    sum_expense,
    min_max_expense,
    monthly_expense_summary,
    average_expense,
    expense_anomalies,
    recurring_expenses,
    check_budget,
    unknown,
]
