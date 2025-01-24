from typing import Optional, List
from typing_extensions import TypedDict
from pydantic import BaseModel
from langchain_core.tools import tool


class ExpenseSchema(TypedDict):
    """
    Schema for representing an expense.
    Attributes:
        id (str): Unique identifier for the expense.
        vector (List[float]): A list of numerical values associated with the expense.
        date (str): The date of the expense in YYYY-MM-DD format.
        amount (float): The amount of money spent in float format.
        category (str): The category of the expense (e.g., food, travel, etc.).
        description (Optional[str]): A brief description of the expense (optional).
    """

    id: str
    vector: List[float]
    date: str
    amount: float
    category: str
    description: Optional[str]


class ExpenseCreate(ExpenseSchema):
    pass


@tool
def create_expense(
    id: str,
    vector: List[float],
    date: str,
    amount: float,
    category: str,
    description: Optional[str] = None,
) -> dict:
    """
    Create an expense dictionary.
    Args:
        id (str): Unique identifier for the expense.
        vector (List[float]): A list of numerical values associated with the expense.
        date (str): The date of the expense in YYYY-MM-DD format.
        amount (float): The amount of money spent in float format.
        category (str): The category of the expense (e.g., food, travel, etc.).
        description (Optional[str]): A brief description of the expense (optional).
    Returns:
        dict: A dictionary representing the expense.
    """
    return {
        "id": id,
        "vector": vector,
        "date": date,
        "amount": amount,
        "category": category,
        "description": description,
    }
