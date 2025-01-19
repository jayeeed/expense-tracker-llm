import os
import uuid
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from qdrant_client.http.models import PointStruct
from app.schemas import ExpenseSchema
from app.qdrant_utils import embedding_model, client
from app.db_utils import save_to_db, get_from_db
from langsmith import traceable
from threading import Thread
from langchain.schema import HumanMessage
from langchain_groq import ChatGroq
from groq import Groq
from PIL import Image
import io
from langchain_core.messages import HumanMessage

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
API_KEY = os.getenv("GROQ_API_KEY")

# llm = ChatAnthropic(
#     model="claude-3-5-sonnet-20240620",
#     temperature=0,
#     api_key=os.getenv("ANTHROPIC_API_KEY"),
# )

llm = ChatGroq(
    api_key=API_KEY,
    model="llama-3.3-70b-versatile",
)

llm_vision = ChatGroq(
    api_key=API_KEY,
    model="llama-3.2-90b-vision-preview",
)


def generate_embedding(user_input: str):
    response = embedding_model.embed_query(text=user_input)
    return response


@traceable
def parse_expense_input(user_input: str, image_url):
    """Parse user input (text or image) and store as embeddings in Qdrant."""
    if image_url:
        # Create a HumanMessage with the image URL
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Extract total expense from the invoice in the following format:\n"
                    "    date: str\n"
                    "    amount: float\n"
                    "    category: str\n"
                    "    description: Optional[str]",
                },
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )

        # Send the message to the model
        expense_data = llm_vision.invoke(message)
        print(expense_data.content)

    else:
        expense_data = llm.with_structured_output(ExpenseSchema).invoke(user_input)

    expense_data.update(
        {"date": datetime.now().strftime("%Y-%m-%d"), "id": uuid.uuid4().hex}
    )
    print("point created: ", expense_data["id"])

    point = PointStruct(
        id=expense_data["id"],
        vector=generate_embedding(user_input),
        payload={
            key: expense_data[key]
            for key in ["date", "amount", "category", "description"]
        },
    )
    client.upsert(points=[point], collection_name=COLLECTION_NAME)

    db_thread = Thread(target=save_to_db, args=(expense_data,))
    db_thread.start()

    return {**expense_data, "vector": point.vector}


@traceable
def search_expense_input(query: str):
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


def detect_intent(user_query: str):
    """Detect the intent of the user query."""
    prompt = f"""
    Determine if the following input describes an expense to save (e.g., a purchase or a transaction) or if it describes a search query for existing expenses. Respond with below options:
    1. Add Expense
    2. Search Expense
    3. Unknown
    Input: "{user_query}"
    Output:
    """
    response = llm.invoke(prompt).content.strip().lower()
    if "add expense" in response:
        return "add_expense"
    elif "search expense" in response:
        return "search_expense"
    else:
        return "unknown"


def add_expense(user_query: str, image_content, image_url):
    """Wrapper for adding expenses."""
    return parse_expense_input(user_query, image_content, image_url)


def search_expense(user_query: str):
    """Wrapper for searching expenses."""
    return search_expense_input(user_query)


# API Mapping
API_MAPPING = {
    "add_expense": add_expense,
    "search_expense": search_expense,
}


def route_request(user_query: str, image_content=None, image_url=None):
    """Route the user query to the appropriate API based on detected intent."""
    intent = detect_intent(user_query)

    if intent == "unknown":
        response = {"response": "Sorry, I couldn't understand your request."}
    elif intent in API_MAPPING:
        response = API_MAPPING[intent](user_query, image_content, image_url)

    return {**response, "intent": intent}
