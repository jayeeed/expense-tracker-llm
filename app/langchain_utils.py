from langchain_ollama import ChatOllama
from app.schemas import ExpenseCreate
from app.qdrant_utils import vectorstore
from qdrant_client.http import models
from langchain.tools import tool
import re

llm = ChatOllama(model="llama3.2:1b")


@tool("extract_expense")
def extract_expense_tool(user_input: str) -> dict:
    """Store expense as embeddings in Qdrant."""
    pattern = (
        r"(?P<amount>\d+)\s+on\s+(?P<category>\w+)(?:\s+for\s+(?P<description>.*))?"
    )
    match = re.match(pattern, user_input.strip())
    if not match:
        raise ValueError("Invalid input format.")
    data = match.groupdict()
    return {
        "amount": int(data["amount"]),
        "category": data["category"],
        "description": user_input,
    }


def parse_expense_input(user_input: str) -> ExpenseCreate:
    """Parse user input and store as embeddings in Qdrant."""
    expense_data = extract_expense_tool.invoke(user_input)
    expense = ExpenseCreate(**expense_data)

    expense_text = f"{expense.amount} spent on {expense.category}, description: {expense.description}"

    vectorstore.add_texts([expense_text])
    return expense


def search_expense(query: str, k: int = 1, category_filter: str = None):
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
