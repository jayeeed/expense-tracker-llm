from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ExpenseSchema(BaseModel):
    date: str = Field(
        default_factory=lambda: datetime.now().date().strftime("%Y-%m-%d")
    )
    amount: int
    category: Optional[str] = None
    description: Optional[str] = None


class ExpenseCreate(ExpenseSchema):
    pass
