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


@tool
def sum_expense(category: str) -> str:
    """Sum expenses by category."""

    query = f"SELECT SUM(amount) FROM expenses WHERE LOWER(category) = '{category}'"

    return db_query(query)


@tool
def min_max_expense(category: str) -> str:
    """Return min and max expenses by category."""

    query = f"SELECT MIN(amount), MAX(amount) FROM expenses WHERE LOWER(category) = '{category}'"

    return db_query(query)


@tool
def monthly_expense_summary(year: int, month: int) -> dict:
    """Get a summary of total expenses per category for a given month."""

    query = f"""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE EXTRACT(YEAR FROM date::DATE) = {year} 
        AND EXTRACT(MONTH FROM date::DATE) = {month}
        GROUP BY category
    """

    return db_query(query)


@tool
def average_expense(category: Optional[str] = None) -> str:
    """Get the average expense amount per category or overall."""

    query = "SELECT category, AVG(amount) FROM expenses"

    if category:
        query += f" WHERE LOWER(category) = '{category}'"

    query += " GROUP BY category"

    return db_query(query)


@tool
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


@tool
def recurring_expenses() -> dict:
    """
    Detect recurring expenses that appear at least `min_count` times.
    """

    query = f"""
        SELECT category, COUNT(*) as occurrences, SUM(amount) as total_spent
        FROM expenses
        GROUP BY category
        HAVING COUNT(*) >= 5
        ORDER BY occurrences DESC
    """

    return db_query(query)


@tool
def check_budget(category: str, budget_limit: float) -> str:
    """Check if expenses in a category exceed a given budget limit."""

    query = f"""
        SELECT SUM(amount) as total_spent FROM expenses WHERE LOWER(category) = '{category}'
    """

    result = db_query(query)  # Returns a list of dictionaries

    if result and result[0]["total_spent"] is not None:
        total_spent = float(result[0]["total_spent"])  # Extract the sum value properly
    else:
        total_spent = 0.0  # Default to 0 if no expenses exist in the category

    if total_spent > budget_limit:
        return f"Warning: You've exceeded your budget for {category}. Spent: {total_spent}, Limit: {budget_limit}"
    else:
        return f"You're within budget for {category}. Spent: {total_spent}, Limit: {budget_limit}"


@tool
def daterange_all_expenses(from_date: str, to_date: str) -> list:
    """Retrieve all expenses within a given date range (inclusive)."""

    query = f"""
        SELECT id, date, amount, category, description
        FROM expenses
        WHERE date::DATE BETWEEN '{from_date}' AND '{to_date}'
        ORDER BY date ASC
    """

    return db_query(query)


@tool
def daterange_category_expenses(category: str, from_date: str, to_date: str) -> list:
    """Retrieve expenses for a specific category within a given date range (inclusive)."""

    query = f"""
        SELECT id, date, amount, category, description
        FROM expenses
        WHERE LOWER(category) = '{category.lower()}'
        AND date::DATE BETWEEN '{from_date}' AND '{to_date}'
        ORDER BY date ASC
    """

    return db_query(query)


@tool
def highest_expense() -> dict:
    """Retrieve the highest expense recorded."""

    query = "SELECT * FROM expenses ORDER BY amount DESC LIMIT 1"
    return db_query(query)


@tool
def lowest_expense() -> dict:
    """Retrieve the lowest expense recorded."""

    query = "SELECT * FROM expenses ORDER BY amount ASC LIMIT 1"
    return db_query(query)


@tool
def category_percentage() -> dict:
    """Calculate the percentage of total expenses spent on each category."""

    query = """
        SELECT category, 
               SUM(amount) AS total_spent, 
               (SUM(amount) * 100 / (SELECT SUM(amount) FROM expenses)) AS percentage
        FROM expenses
        GROUP BY category
        ORDER BY percentage DESC
    """

    return db_query(query)


@tool
def yearly_expense_summary(year: int) -> dict:
    """Summarize total expenses per category for a given year."""

    query = f"""
        SELECT category, SUM(amount) AS total_spent
        FROM expenses
        WHERE EXTRACT(YEAR FROM date::DATE) = {year}
        GROUP BY category
        ORDER BY total_spent DESC
    """

    return db_query(query)


@tool
def expense_trends(interval: str = "monthly") -> dict:
    """
    Identify expense trends over time.
    `interval` can be 'monthly' or 'yearly'.
    """

    if interval == "monthly":
        query = """
            SELECT EXTRACT(YEAR FROM date::DATE) AS year, 
                   EXTRACT(MONTH FROM date::DATE) AS month, 
                   SUM(amount) AS total_spent
            FROM expenses
            GROUP BY year, month
            ORDER BY year DESC, month DESC
        """
    else:
        query = """
            SELECT EXTRACT(YEAR FROM date::DATE) AS year, 
                   SUM(amount) AS total_spent
            FROM expenses
            GROUP BY year
            ORDER BY year DESC
        """

    return db_query(query)


@tool
def predict_future_expenses(months_ahead: int) -> dict:
    """
    Estimate future expenses based on historical data.
    Uses an average of past monthly expenses to predict expenses for upcoming months.
    """

    query = """
        WITH monthly_avg AS (
            SELECT EXTRACT(YEAR FROM date::DATE) AS year,
                   EXTRACT(MONTH FROM date::DATE) AS month,
                   SUM(amount) AS total_spent
            FROM expenses
            GROUP BY year, month
        )
        SELECT AVG(total_spent) AS predicted_expense
        FROM monthly_avg
    """

    result = db_query(query)
    print(result)

    if result and result[0]["predicted_expense"] is not None:
        avg_expense = float(result[0]["predicted_expense"])
        predictions = {
            f"Month {i+1}": round(avg_expense, 2) for i in range(months_ahead)
        }
        return predictions
    else:
        return {"message": "Not enough data to predict future expenses."}


@tool
def compare_periods_expenses(
    from_date_1: str,
    to_date_1: str,
    from_date_2: str,
    to_date_2: str,
) -> dict:
    """
    Compare the total expenses between two date ranges.
    Returns the totals for each period, the difference, and the percentage change.
    """
    query1 = f"SELECT SUM(amount) AS total_spent FROM expenses WHERE date::DATE BETWEEN '{from_date_1}' AND '{to_date_1}'"
    query2 = f"SELECT SUM(amount) AS total_spent FROM expenses WHERE date::DATE BETWEEN '{from_date_2}' AND '{to_date_2}'"

    result1 = db_query(query1)
    result2 = db_query(query2)

    total1 = (
        float(result1[0]["total_spent"])
        if result1 and result1[0]["total_spent"] is not None
        else 0.0
    )
    total2 = (
        float(result2[0]["total_spent"])
        if result2 and result2[0]["total_spent"] is not None
        else 0.0
    )

    difference = total2 - total1
    percent_change = ((difference / total1) * 100) if total1 != 0 else None

    return {
        "period_1": {
            "from_date": from_date_1,
            "to_date": to_date_1,
            "total_spent": total1,
        },
        "period_2": {
            "from_date": from_date_2,
            "to_date": to_date_2,
            "total_spent": total2,
        },
        "difference": difference,
        "percent_change": percent_change,
    }


@tool
def recent_expenses(limit: int) -> dict:
    """Return the most recent expenses."""

    query = f"SELECT * FROM expenses ORDER BY date DESC LIMIT {limit}"

    return db_query(query)


@tool
def suggest_savings() -> str:
    """
    Suggest which expense category to reduce spending on in order to save money.
    This tool calculates the average expense per category and identifies the category
    with the highest average expense.
    """
    query = """
        SELECT category, AVG(amount) AS avg_spent
        FROM expenses
        GROUP BY category
        ORDER BY avg_spent DESC
        LIMIT 1
    """
    result = db_query(query)

    if result and result[0]["avg_spent"] is not None:
        highest_category = result[0]["category"]
        highest_avg = float(result[0]["avg_spent"])
        return (
            f"To save money, consider reducing your spending on the '{highest_category}' category. "
            f"Your average expense in this category is {highest_avg:.2f}, which is the highest among all categories."
        )
    else:
        return "Not enough data to provide a savings suggestion."


@tool
def encourage_spending() -> dict:
    """Encourage the user to increase their expenses on specific categories."""

    query = """
        SELECT category, AVG(amount) AS avg_spent
        FROM expenses
        GROUP BY category
        ORDER BY avg_spent ASC
        LIMIT 1
    """

    result = db_query(query)

    if result and result[0]["avg_spent"] is not None:
        lowest_category = result[0]["category"]
        lowest_avg = float(result[0]["avg_spent"])
        return (
            f"Consider increasing your spending on the '{lowest_category}' category. "
            f"Your average expense in this category is {lowest_avg:.2f}, which is the lowest among all categories."
        )
    else:
        return "Not enough data to provide an encouragement."


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
    sum_expense,
    min_max_expense,
    monthly_expense_summary,
    average_expense,
    expense_anomalies,
    recurring_expenses,
    check_budget,
    daterange_all_expenses,
    daterange_category_expenses,
    highest_expense,
    lowest_expense,
    category_percentage,
    yearly_expense_summary,
    expense_trends,
    predict_future_expenses,
    compare_periods_expenses,
    recent_expenses,
    suggest_savings,
    encourage_spending,
    greetings,
    unknown,
]
