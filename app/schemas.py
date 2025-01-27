from typing import List, Annotated
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


class ExpenseSearch(TypedDict):
    """Generate sql query for searching expenses on postgres db."""

    query: Annotated[str, ..., "SQL query for searching expenses on postgres db."]


class ExpenseSearchResponse(TypedDict):
    """Response for searching expenses on postgres db."""

    response: Annotated[str, ..., "Explain query output in short general language."]
