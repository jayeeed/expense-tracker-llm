import os
import uuid
from datetime import datetime
from qdrant_client.http.models import PointStruct
from app.schemas import ExpenseSchema
from app.qdrant_utils import embedding_model, client
from app.db_utils import save_to_db, get_from_db
from langsmith import traceable
from threading import Thread
from langchain_groq import ChatGroq
from app.tools import image_tool

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=100,
)

llm_vision = ChatGroq(
    api_key=API_KEY,
    model="llama-3.2-90b-vision-preview",
    temperature=0.1,
    max_tokens=100,
)


def generate_embedding(user_input: str):
    response = embedding_model.embed_query(text=user_input)
    return response


# TODO: Add tool calling logic here
@traceable
def parse_expense_input(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Parse user input (text or image) and store as embeddings in Qdrant."""
    if image_url or image_content:
        input_data = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Simply extract data from the image as below format:\n"
                            "    date: str (e.g., '2023-10-01')\n"
                            "    amount: float (e.g., 23.45)\n"
                            "    category: str (e.g., 'Food')\n"
                            "    description: str (e.g., 'Lunch at restaurant')"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": (
                                image_url
                                if image_url
                                else f"data:image/jpeg;base64,{image_content}"
                            )
                        },
                    },
                ],
            },
        ]

        expense_data_unstruct = llm_vision.invoke(input_data)
        expense_data = llm.with_structured_output(ExpenseSchema).invoke(
            expense_data_unstruct.content
        )

    else:
        expense_data = llm.with_structured_output(ExpenseSchema).invoke(user_input)

    expense_data.update(
        {"date": datetime.now().strftime("%Y-%m-%d"), "id": uuid.uuid4().hex}
    )
    print("point created: ", expense_data["id"])

    point = PointStruct(
        id=expense_data["id"],
        vector=generate_embedding(user_input or image_url or image_content),
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
def search_expense_input(user_input: str):
    """Search for similar expenses stored in Qdrant with optional category filtering."""

    # Perform similarity search with scores
    results_with_scores = client.search(
        query_vector=generate_embedding(user_input),
        collection_name=COLLECTION_NAME,
    )

    # Process and filter results
    filtered_results = []
    for result in results_with_scores:
        if result.score > 0.5:
            filtered_results.append(result.payload)

    return filtered_results[0]


def route_request(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Route the request to either add or search for expenses based on intent."""
    if image_content or image_url:
        return parse_expense_input(image_content=image_content, image_url=image_url)

    intent_detection_prompt = (
        "You are an intent detection model. Classify the following input as one of these options:\n"
        "add_expense, search_expense, or unknown.\n"
        f"Input: {user_input}\n"
        "Output (one of: add_expense, search_expense, unknown):"
    )
    intent_response = llm.invoke(intent_detection_prompt).content.strip().lower()
    intent = (
        intent_response.split()[-1]
        if intent_response in ["add_expense", "search_expense", "unknown"]
        else "unknown"
    )
    print("intent detected: ", intent)

    if intent == "add_expense":
        return parse_expense_input(user_input=user_input)

    elif intent == "search_expense":
        return search_expense_input(user_input=user_input)

    elif intent == "unknown":
        return {"error": "Could not determine intent. Please try again."}

    return {"error": "Could not determine intent. Please try again."}
