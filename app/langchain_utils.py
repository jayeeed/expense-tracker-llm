import os
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from qdrant_client.http import models
from app.schemas import ExpenseSchema
from app.qdrant_utils import vectorstore
from langsmith import traceable

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


@traceable
def parse_expense_input(user_input: str):
    """Parse user input and store as embeddings in Qdrant."""
    structured_llm = llm.with_structured_output(ExpenseSchema)

    expense_data = structured_llm.invoke(user_input)

    expense_data["date"] = datetime.now().strftime("%Y-%m-%d")
    expense = ExpenseSchema(**expense_data)

    expense_text = f"Date: {expense['date']}, Amount: {expense['amount']}, Category: {expense['category']}, Description: {expense['description']}"

    vectorstore.add_texts([expense_text])
    return expense


@traceable
def search_expense(query: str, k: int = 10, category_filter: str = None):
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
        if result[1] > 0.6
    ]

    # Calculate total amount from filtered results
    total_amount = 0
    for result in filtered_results:
        try:
            amount_str = result["content"].split("Amount:")[1].split(",")[0].strip()
            total_amount += float(amount_str)
        except (IndexError, ValueError):
            continue

    return {
        "results": (
            filtered_results
            if filtered_results
            else [{"message": "No matching results found."}]
        ),
        "total_amount": total_amount,
    }
