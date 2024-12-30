import os
from datetime import datetime
import uuid
from langchain_anthropic import ChatAnthropic
from qdrant_client.http.models import PointStruct
from app.schemas import ExpenseSchema
from app.qdrant_utils import embedding_model, client
from langsmith import traceable

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

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
    client.upsert(points=[point], collection_name=COLLECTION_NAME)

    return {**expense_data, "vector": point.vector}


@traceable
def search_expense(query: str):
    """Search for similar expenses stored in Qdrant with optional category filtering."""

    # Perform similarity search with scores
    results_with_scores = client.search(
        query_vector=generate_embedding(query),
        collection_name=COLLECTION_NAME,
    )

    # Process and filter results
    filtered_results = []
    for result in results_with_scores:
        if result.score > 0.5:
            filtered_results.append(result.payload)

    return filtered_results[0]


def decide_user_intent(user_input: str):
    """
    Use LLM to determine whether the user's intent is to save a new expense or search for an existing one.
    """
    # Define a prompt to guide the LLM's decision-making
    intent_prompt = (
        "Determine if the following input describes an expense to save (e.g., a purchase or a transaction) "
        "or if it describes a search query for existing expenses. Respond with either 'save' or 'search'.\n"
        f"Input: {user_input}\n"
        "Output:"
    )

    # Use the LLM to analyze the intent
    response = llm.invoke(intent_prompt)

    # Extract the text content from the AIMessage object
    intent = response.content.strip().lower()

    if intent not in ["save", "search"]:
        raise ValueError(
            "Unable to determine user intent. Please try rephrasing your input."
        )

    return intent


def process_user_input(user_input: str):
    """
    Process the user's input by determining the intent and executing the appropriate function.
    """
    intent = decide_user_intent(user_input)

    if intent == "save":
        return parse_expense_input(user_input)
    elif intent == "search":
        return search_expense(user_input)
    else:
        raise ValueError("Unexpected intent result.")
