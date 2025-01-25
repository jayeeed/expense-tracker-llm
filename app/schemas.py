from typing import List
from typing_extensions import TypedDict
from enum import Enum


class ExpenseCategory(str, Enum):
    """Enum for representing expense categories."""

    FOOD = "Food"
    TRAVEL = "Travel"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    GROCERY = "Grocery"
    SHOPPING = "Shopping"
    ELECTRONICS = "Electronics"
    HEALTH = "Health"
    MISCELLANEOUS = "Miscellaneous"


class ExpenseSchema(TypedDict):
    """Schema for representing an expense."""

    id: str
    vector: List[float]
    date: str
    amount: float
    category: ExpenseCategory
    description: str


class ExpenseCreate(ExpenseSchema):
    pass


class ExpenseSearch(TypedDict):
    """Generate sql query for searching expenses on postgres db."""

    query: str
