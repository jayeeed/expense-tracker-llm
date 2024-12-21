from typing import Optional
from typing_extensions import TypedDict


class ExpenseSchema(TypedDict):
    date: str
    amount: int
    category: str
    description: Optional[str]


class ExpenseCreate(ExpenseSchema):
    pass


tools = [ExpenseSchema]
