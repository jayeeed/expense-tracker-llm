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


class IntentCategory(str, Enum):
    """Enum for representing intent categories."""

    ADD_EXPENSE = "add_expense"
    SEARCH_EXPENSE = "search_expense"
    UNKNOWN = "unknown"


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
    """Generate sql query for searching expenses."""

    query: Annotated[str, ..., "SQL query for searching expenses on postgres db."]


class ExpenseSearchResponse(TypedDict):
    """Response for searching expenses."""

    response: Annotated[str, ..., "Explain query output in short general language."]


class IntentDetection(TypedDict):
    """Detect intent from user input."""

    intent: Annotated[IntentCategory, ..., "Intent detected from user input."]
