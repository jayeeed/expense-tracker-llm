from langchain_ollama import ChatOllama
from app.schemas import ExpenseCreate
from app.qdrant_utils import vectorstore
from qdrant_client.http import models
from datetime import datetime
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:1b")

json_schema = {
    "title": "ExpenseCreate",
    "description": "Schema for storing expense data",
    "type": "object",
    "properties": {
        "amount": {
            "type": "integer",
            "description": "Amount of the expense. e.g. 100, 200, 500, etc. Ignore non-numeric characters.",
        },
        "category": {
            "type": "string",
            "description": "Type of category for the expense. e.g. Food, Travel, Groceries, etc.",
            "default": "General",
        },
        "description": {
            "type": "string",
            "description": "Short summary of the expense",
            "default": "No description",
        },
    },
    "required": ["amount", "category"],
}


def parse_expense_input(user_input: str) -> ExpenseCreate:
    """Parse user input and store as embeddings in Qdrant."""
    structured_llm = llm.with_structured_output(json_schema)
    print(structured_llm)
    expense_data = structured_llm.invoke(user_input)
    print(expense_data)

    expense = ExpenseCreate(
        date=datetime.now().strftime("%Y-%m-%d"),
        amount=expense_data.get("amount"),
        category=expense_data.get("category"),
        description=expense_data.get("description", "No description"),
    )

    expense_text = (
        f"Date: {expense.date}, Amount: {expense.amount}, "
        f"Category: {expense.category}, Description: {expense.description}"
    )

    vectorstore.add_texts([expense_text])
    return expense


def search_expense(query: str, k: int = 3, category_filter: str = None):
    """Search for similar expenses stored in Qdrant with optional category filtering."""
    qdrant_filter = None
    if category_filter:
        qdrant_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="category", match=models.MatchValue(value=category_filter)
                )
            ]
        )

    # Perform similarity search with scores
    results_with_scores = vectorstore.similarity_search_with_score(
        query=query, k=k, filter=qdrant_filter
    )

    # Process and filter results
    filtered_results = [
        {"content": result[0].page_content, "score": result[1]}
        for result in results_with_scores
        if result[1] <= 1
    ]

    return (
        filtered_results
        if filtered_results
        else [{"message": "No matching results found."}]
    )
