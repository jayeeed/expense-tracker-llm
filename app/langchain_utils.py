import os
import uuid
from datetime import datetime
import dateparser
from app.tool_factory import tools
from app.db_utils import save_to_db
from langsmith import traceable
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from app.tool_factory import *

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

llm_with_tools = llm.bind_tools(tools)

llm_vision = ChatGroq(
    api_key=API_KEY,
    model="llama-3.2-90b-vision-preview",
    temperature=0.1,
)

SEARCH_FUNCTIONS = {
    "search_expense": search_by_fields,
}


@traceable
def route_request(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Route the request to either add or search for expenses based on intent."""

    if image_content or image_url:
        input_data = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Simply extract data from the image in the following format:\n"
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
        expense_data_dict = llm_with_tools.invoke(expense_data_unstruct.content)
        expense_data = expense_data_dict.tool_calls[0]["args"]

        return {"intent": "add_expense", "result": parse_expense_input(expense_data)}

    current_date = datetime.now().strftime("%Y-%m-%d")
    user_input_with_date = f"{user_input} (Current Date: {current_date})"

    ai_msg = [HumanMessage(user_input_with_date)]
    intent_response = llm_with_tools.invoke(ai_msg)
    intent = intent_response.tool_calls[0]["name"]
    print("Intent:", intent)
    parsed_input = intent_response.tool_calls[0]["args"]
    print("Parsed Input:", parsed_input)

    if intent == "add_expense":
        result = parse_expense_input(parsed_input)
    elif intent in SEARCH_FUNCTIONS:
        tool_function = SEARCH_FUNCTIONS[intent]
        result_response = tool_function.invoke(parsed_input)
        if result_response == []:
            result = "No results found."
        else:
            result = llm.invoke(
                f"Explain response in general language (max 20 words): {result_response}."
            )
            result_content = result.content
            start_idx = result_content.find("<think>")
            end_idx = result_content.find("</think>") + len("</think>")
            if start_idx != -1 and end_idx != -1:
                result_content = result_content[:start_idx] + result_content[end_idx:]

            result = result_content.strip()
    else:
        result = {"error": "Could not determine intent. Please try again."}

    return {"intent": intent, "result": result}


@traceable
def parse_expense_input(expense_data: dict):
    """Parse structured expense data and store it in the database."""

    if not expense_data.get("date"):
        expense_data["date"] = datetime.now().strftime("%Y-%m-%d")
    expense_data["id"] = uuid.uuid4().hex
    save_to_db(expense_data)

    return expense_data


@traceable
def get_from_pgdb(query: str):
    """Get the expense data from the database."""

    response = llm_with_tools.invoke(query)
    return response
