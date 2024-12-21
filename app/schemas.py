from pydantic import BaseModel
from typing import Optional
from typing_extensions import Annotated, TypedDict


class ExpenseSchema(BaseModel):
    date: Annotated[str, ..., "Date of the expense. e.g. 2024-12-01"]
    amount: Annotated[
        int,
        ...,
        "Amount of the expense. e.g. 100, 200, 500, etc. Ignore non-numeric characters.",
    ]
    category: Annotated[
        str, ..., "Type of category for the expense. e.g. Food, Travel, Groceries, etc."
    ]
    description: Annotated[
        Optional[str],
        ...,
        "Short summary of the expense e.g. Lunch at Banani.",
    ]


class ExpenseCreate(ExpenseSchema):
    pass


tools = [ExpenseCreate]
