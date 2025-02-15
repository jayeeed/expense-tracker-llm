from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict, List
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


# 2. Insert a new expense record
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


# 3. Select all expenses
@tool
def get_all_expenses() -> Dict[str, Any]:
    """
    Returns all expense records.
    """
    query = "SELECT * FROM expenses"

    print("SQL:", query)

    return db_query(query)


# 4. Filter expenses by category
@tool
def get_expenses_by_category(category: Category) -> Dict[str, Any]:
    """
    Returns expenses filtered by category.
    """
    query = f"SELECT * FROM expenses WHERE category = '{category.value}'"

    print("SQL:", query)

    return db_query(query)


# 5. Filter expenses by a date range
@tool
def get_expenses_by_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Returns expenses that fall between start_date and end_date.
    """
    query = f"SELECT * FROM expenses WHERE date BETWEEN '{start_date}' AND '{end_date}'"

    print("SQL:", query)

    return db_query(query)


# 6. Filter expenses above a given amount in descending order
@tool
def get_expenses_above_amount(min_amount: float) -> Dict[str, Any]:
    """
    Returns expenses with amount greater than min_amount in descending order.
    """
    query = f"SELECT * FROM expenses WHERE amount > {min_amount} ORDER BY amount DESC"

    print("SQL:", query)

    return db_query(query)


# 7. Sort expenses by a specified column and order
@tool
def get_sorted_expenses(order_by: str = "date", order: str = "DESC") -> Dict[str, Any]:
    """
    Returns expenses sorted by the specified column and order.
    Only allows ordering by specific columns.
    """
    allowed_columns = {"date", "amount", "category", "description"}
    if order_by not in allowed_columns:
        return {"error": "Invalid order_by column"}
    order = order.upper()
    if order not in {"ASC", "DESC"}:
        return {"error": "Invalid order"}
    query = f"SELECT * FROM expenses ORDER BY {order_by} {order}"

    print("SQL:", query)

    return db_query(query)


# 8. Limit the number of returned expense records
@tool
def get_limited_expenses(
    limit: int, order_by: str = "date", order: str = "DESC"
) -> Dict[str, Any]:
    """
    Returns a limited number of expense records.
    """
    allowed_columns = {"date", "amount", "category", "description"}
    if order_by not in allowed_columns:
        return {"error": "Invalid order_by column"}
    order = order.upper()
    if order not in {"ASC", "DESC"}:
        return {"error": "Invalid order"}
    query = f"SELECT * FROM expenses ORDER BY {order_by} {order} LIMIT {limit}"

    print("SQL:", query)

    return db_query(query)


# 9. Aggregate: Sum of amounts by category
@tool
def aggregate_sum_by_category() -> Dict[str, Any]:
    """
    Returns the sum of amounts for each category.
    """
    query = """
    SELECT category, SUM(amount) AS total_amount
    FROM expenses
    GROUP BY category
    """

    print("SQL:", query)

    return db_query(query)


# 10. Aggregate: Count expenses by category
@tool
def count_expenses_by_category() -> Dict[str, Any]:
    """
    Returns the count of expenses for each category.
    """
    query = """
    SELECT category, COUNT(*) AS expenses_count
    FROM expenses
    GROUP BY category
    """

    print("SQL:", query)

    return db_query(query)


# 11. Aggregate with HAVING: Only include categories whose sum exceeds a given value
@tool
def aggregate_with_having(min_total: float) -> Dict[str, Any]:
    """
    Returns categories where the total amount exceeds min_total.
    """
    query = f"""
    SELECT category, SUM(amount) AS total_amount
    FROM expenses
    GROUP BY category
    HAVING SUM(amount) > {min_total}
    """

    print("SQL:", query)

    return db_query(query)


# 12. Subquery: Select expenses with amount above the overall average
@tool
def get_expenses_above_average() -> Dict[str, Any]:
    """
    Returns expenses where the amount is above the overall average.
    """
    query = """
    SELECT *
    FROM expenses
    WHERE amount > (SELECT AVG(amount) FROM expenses)
    """

    print("SQL:", query)

    return db_query(query)


# 13. CTE: Use a Common Table Expression to filter by aggregated totals
@tool
def get_expenses_with_cte(min_total: float) -> Dict[str, Any]:
    """
    Returns categories (and their totals) where the total amount is above min_total,
    using a CTE.
    """
    query = f"""
    WITH category_totals AS (
        SELECT category, SUM(amount) AS total_amount
        FROM expenses
        GROUP BY category
    )
    SELECT *
    FROM category_totals
    WHERE total_amount > {min_total}
    """

    print("SQL:", query)

    return db_query(query)


# 14. Window Function: Running total per category
@tool
def get_expenses_with_running_total() -> Dict[str, Any]:
    """
    Returns expenses along with a running total per category.
    """
    query = """
    SELECT date, amount, category, description,
           SUM(amount) OVER (PARTITION BY category ORDER BY date) AS running_total
    FROM expenses
    """

    print("SQL:", query)

    return db_query(query)


# 17. Distinct: Get unique expense categories
@tool
def get_distinct_categories() -> Dict[str, Any]:
    """
    Returns a list of distinct expense categories.
    """
    query = "SELECT DISTINCT category FROM expenses"

    print("SQL:", query)

    return db_query(query)


# 18. UNION: Combine expenses from two different categories
@tool
def union_expenses_by_categories(
    category1: Category, category2: Category
) -> Dict[str, Any]:
    """
    Returns expenses for two categories combined using UNION.
    """
    query = f"""
    SELECT * FROM expenses WHERE category = '{category1.value}'
    UNION
    SELECT * FROM expenses WHERE category = '{category2.value}'
    """

    print("SQL:", query)

    return db_query(query)


# 20. Full-Text Search: Search expenses by description using a LIKE query
@tool
def partial_text_search_expenses(search_term: str) -> Dict[str, Any]:
    """
    Returns expenses where the description matches the search term using a LIKE query.
    """
    query = f"""
    SELECT *
    FROM expenses
    WHERE description LIKE '%{search_term}%'
    """

    print("SQL:", query)

    return db_query(query)


# 21. Advanced Example: Using a CASE expression for conditional output
@tool
def advanced_case_expenses() -> Dict[str, Any]:
    """
    Returns expenses with an additional column 'expenses_type' that labels
    the expenses as Credit, Debit, or Neutral based on the amount.
    """
    query = """
    SELECT date,
           amount,
           category,
           description,
           CASE 
               WHEN amount > 0 THEN 'Credit'
               WHEN amount < 0 THEN 'Debit'
               ELSE 'Neutral'
           END AS expenses_type
    FROM expenses
    """

    print("SQL:", query)

    return db_query(query)


# 22. Self-Join: Compare each expense to the previous day's expense
@tool
def self_join_previous_day_expenses() -> Dict[str, Any]:
    """
    Returns expenses along with the previous day's amount (if any) by self-joining the table.
    """
    query = """
    SELECT a.date, a.amount, a.category, a.description,
           b.amount AS previous_day_amount
    FROM expenses a
    LEFT JOIN expenses b
      ON b.date = a.date - INTERVAL '1 day'
    """

    print("SQL:", query)

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
    get_all_expenses,
    get_expenses_by_category,
    get_expenses_by_date_range,
    get_expenses_above_amount,
    get_sorted_expenses,
    get_limited_expenses,
    aggregate_sum_by_category,
    count_expenses_by_category,
    aggregate_with_having,
    get_expenses_above_average,
    get_expenses_with_cte,
    get_expenses_with_running_total,
    get_distinct_categories,
    union_expenses_by_categories,
    partial_text_search_expenses,
    advanced_case_expenses,
    self_join_previous_day_expenses,
    greetings,
    unknown,
]
