from langchain_ollama import ChatOllama
from app.schemas import ExpenseSchema
from app.json_schemas import json_schema
from app.qdrant_utils import vectorstore
from qdrant_client.http import models
from datetime import datetime
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.2:1b")


def parse_expense_input(user_input: str) -> ExpenseSchema:
    """Parse user input and store as embeddings in Qdrant."""
    structured_llm = llm.with_structured_output(json_schema)

    expense_data = structured_llm.invoke(user_input)

    if not expense_data.get("date"):
        expense_data["date"] = datetime.now().strftime("%Y-%m-%d")
    if not expense_data.get("category"):
        expense_data["category"] = "General"
    if not expense_data.get("description"):
        expense_data["description"] = "No description provided."

    expense = ExpenseSchema(
        date=expense_data["date"],
        amount=expense_data["amount"],
        category=expense_data["category"],
        description=expense_data["description"],
    )

    expense_text = f"Date: {expense['date']}, Amount: {expense['amount']}, Category: {expense['category']}, Description: {expense['description']}"

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
        if result[1] < 0.9
    ]

    return (
        filtered_results
        if filtered_results
        else [{"message": "No matching results found."}]
    )
