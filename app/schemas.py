from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ExpenseSchema(BaseModel):
    log_date: str = Field(
        default_factory=lambda: datetime.now().date().strftime("%Y-%m-%d"),
        description="The date of the expense",
    )
    category: str = Field(description="Category of the expense")
    amount: int = Field(description="Amount spent")
    description: str | None = Field(
        default=None, description="Description of the expense"
    )


class ExpenseCreate(ExpenseSchema):
    pass


class ExpenseQuerySchema(BaseModel):
    date: Optional[str] = Field(
        default=None, description="Filter expenses by date in YYYY-MM-DD format"
    )
    category: Optional[str] = Field(
        default=None, description="Filter expenses by category"
    )
    amount: Optional[float] = Field(
        default=None, description="Filter expenses by amount spent"
    )
    description: Optional[str] = Field(
        default=None, description="Filter expenses by description keyword"
    )


class Expense(ExpenseSchema):
    id: int

    class Config:
        from_attributes = True
