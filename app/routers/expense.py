from fastapi import APIRouter
from app import schemas, langchain_utils

router = APIRouter()


@router.post("/save-expense/", response_model=schemas.ExpenseCreate)
def create_expense(user_input: str):
    """Parse user input and store as embeddings in Qdrant."""
    expense_data = langchain_utils.parse_expense_input(user_input)
    return expense_data


@router.get("/search-expenses/")
def search_expenses(query: str):
    """Search expenses using semantic similarity."""
    results = langchain_utils.search_expense(query)
    return {"results": results}
