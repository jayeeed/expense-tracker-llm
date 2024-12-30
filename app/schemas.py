from typing import Optional, List
from typing_extensions import TypedDict


class ExpenseSchema(TypedDict):
    id: str
    vector: List[float]
    date: str
    amount: int
    category: str
    description: Optional[str]


class ExpenseCreate(ExpenseSchema):
    pass


tools = [ExpenseSchema]
