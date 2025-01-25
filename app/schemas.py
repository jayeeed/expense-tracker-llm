from typing import List
from typing_extensions import TypedDict
from enum import Enum


class ExpenseCategory(str, Enum):
    """Enum for representing expense categories."""

    FOOD = "food"
    TRAVEL = "travel"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    GROCERY = "grocery"
    SHOPPING = "shopping"
    ELECTRONICS = "electronics"
    HEALTH = "health"
    MISCELLANEOUS = "miscellaneous"


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
