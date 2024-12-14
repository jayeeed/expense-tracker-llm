from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas, langchain_utils
from app.database import get_db

router = APIRouter()


@router.post("/save-expense/", response_model=schemas.Expense)
def create_expense(user_input: str, db: Session = Depends(get_db)):
    expense_data = langchain_utils.parse_expense_input(user_input)
    return crud.create_expense(db=db, expense=expense_data)


@router.get("/get-expenses/")
def read_expenses(user_input: str, db: Session = Depends(get_db)):
    query = db.query(models.Expense)
    query = query.filter(
        (models.Expense.amount == user_input)
        | (models.Expense.category.ilike(f"%{user_input}%"))
        | (models.Expense.date == user_input)
        | (models.Expense.description.ilike(f"%{user_input}%"))
    )

    expenses = query.all()
    if not expenses:
        return "No expenses found matching your query."

    responses = [
        f"{expense.amount} taka spent on {expense.category} at {expense.date} for {expense.description}"
        for expense in expenses
    ]
    return responses
