import os
from datetime import datetime
import uuid
from langchain_anthropic import ChatAnthropic
from qdrant_client.http.models import PointStruct, FieldCondition, Filter, MatchValue
from app.schemas import ExpenseSchema
from app.qdrant_utils import vectorstore, embedding_model, client
from langsmith import traceable

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)


def generate_embedding(user_input: str):
    response = embedding_model.embed_query(text=user_input)
    return response


@traceable
def parse_expense_input(user_input: str):
    """Parse user input and store as embeddings in Qdrant."""
    expense_data = llm.with_structured_output(ExpenseSchema).invoke(user_input)
    expense_data.update(
        {"date": datetime.now().strftime("%Y-%m-%d"), "id": uuid.uuid4().hex}
    )

    point = PointStruct(
        id=expense_data["id"],
        vector=generate_embedding(user_input),
        payload={
            key: expense_data[key]
            for key in ["date", "amount", "category", "description"]
        },
    )
    client.upsert(points=[point], collection_name=vectorstore.collection_name)

    return {**expense_data, "vector": point.vector}


@traceable
def search_expense(query: str, k: int = 10, category_filter: str = None):
    """Search for similar expenses stored in Qdrant with optional category filtering."""
    qdrant_filter = None
    if category_filter:
        qdrant_filter = Filter(
            must=[
                FieldCondition(key="Category", match=MatchValue(value=category_filter))
            ]
        )

    # Perform similarity search with scores
    results_with_scores = vectorstore.similarity_search_with_score(
        query=query, k=k, filter=qdrant_filter
    )

    # Process and filter results
    filtered_results = []
    for result in results_with_scores:
        content = result[0].page_content
        print(content)
        score = result[1]

        if score < 1:
            try:
                # Extract fields from content
                fields = {
                    "Date": content.split("Date:")[1].split(",")[0].strip(),
                    "Amount": int(content.split("Amount:")[1].split(",")[0].strip()),
                    "Category": content.split("Category:")[1].split(",")[0].strip(),
                    "Description": content.split("Description:")[1].strip(),
                }
                filtered_results.append({"fields": fields, "score": score})
            except (IndexError, ValueError):
                continue

    # Calculate total amount from filtered results
    total_amount = sum(
        result["fields"]["Amount"]
        for result in filtered_results
        if "Amount" in result["fields"]
    )

    return {
        "results": (
            filtered_results
            if filtered_results
            else [{"message": "No matching results found."}]
        ),
        "total_amount": total_amount,
    }
