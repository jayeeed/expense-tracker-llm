from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ExpenseSchema(BaseModel):
    date: str = Field(
        default_factory=lambda: datetime.now().date().strftime("%Y-%m-%d"),
        description="The date of the expense",
    )
    amount: Optional[float] = Field(description="The amount spent")
    category: Optional[str] = Field(description="The category of the expense")
    description: Optional[str] = Field(description="A brief description of the expense")


class ExpenseCreate(ExpenseSchema):
    pass
