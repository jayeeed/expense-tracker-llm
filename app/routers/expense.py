from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas, langchain_utils
from app.database import get_db

router = APIRouter()


@router.post("/save-expense/", response_model=schemas.Expense)
def create_expense(user_input: str, db: Session = Depends(get_db)):
    expense_data = langchain_utils.parse_expense_input(user_input)
    return crud.create_expense(db=db, expense=expense_data)


@router.get("/expenses/", response_model=list[schemas.Expense])
def read_expenses(user_input: str, db: Session = Depends(get_db)):
    query_params = langchain_utils.parse_query_input(user_input)

    query = db.query(models.Expense)

    filters_applied = False
    if query_params.date:
        query = query.filter(models.Expense.log_date == query_params.date)
        filters_applied = True
    if query_params.category:
        query = query.filter(models.Expense.category == query_params.category)
        filters_applied = True
    if query_params.amount is not None:
        query = query.filter(models.Expense.amount == query_params.amount)
        filters_applied = True
    if query_params.description:
        query = query.filter(models.Expense.description == query_params.description)
        filters_applied = True

    if not filters_applied:
        raise HTTPException(status_code=404, detail="No expense found")

    expenses = query.all()

    if not expenses:
        raise HTTPException(status_code=404, detail="No expense found")

    return expenses
