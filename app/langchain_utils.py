import os
import uuid
from datetime import datetime
from qdrant_client.http.models import PointStruct
from app.schemas import ExpenseSchema, ExpenseSearch, ExpenseSearchResponse
from app.qdrant_utils import embedding_model, client
from app.db_utils import save_to_db, db_query
from langsmith import traceable
from threading import Thread
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
API_KEY = os.getenv("GROQ_API_KEY")

# llm = ChatOllama(
#     model="llama3.1:8b-instruct-q4_1",
#     temperature=0.1,
# )

# llm = ChatAnthropic(
#     api_key=os.getenv("ANTHROPIC_API_KEY"),
#     model="claude-3-5-sonnet-20240620",
#     temperature=0.1,
# )


llm = ChatGroq(
    api_key=API_KEY,
    model="deepseek-r1-distill-llama-70b",
    temperature=0.1,
)

llm_vision = ChatGroq(
    api_key=API_KEY,
    model="llama-3.2-90b-vision-preview",
    temperature=0.1,
)


def generate_embedding(user_input: str):
    response = embedding_model.embed_query(text=user_input)
    return response


@traceable
def parse_expense_input(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Parse user input image and store as embeddings in Qdrant."""
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
def get_from_vectordb(user_input: str):
    """Search for similar expenses stored in Qdrant with optional category filtering."""
    results_with_scores = client.search(
        query_vector=generate_embedding(user_input),
        collection_name=COLLECTION_NAME,
    )

    filtered_results = []
    for result in results_with_scores:
        if result.score > 0.5:
            filtered_results.append(result.payload)

    return filtered_results[0]


# @traceable
# def get_from_pgdb(user_input):
#     """Get the expense data from the database."""
#     db_uri = os.getenv("POSTGRES_URL")
#     db = SQLDatabase.from_uri(db_uri)
#     toolkit = SQLDatabaseToolkit(db=db, llm=llm)
#     agent = create_sql_agent(
#         llm=llm,
#         toolkit=toolkit,
#         verbose=True,
#     )
#     result = agent.invoke(user_input)

#     return result


@traceable
def get_from_pgdb(user_input: str):
    """Get the expense data from the database."""
    response = llm.with_structured_output(ExpenseSearch).invoke(user_input)
    query = response["query"]
    output = db_query(query.lower())
    result = llm.with_structured_output(ExpenseSearchResponse).invoke(f"{output}")

    return result["response"]
