import os
import re
import uuid
from datetime import datetime
from app.tool_factory import tools
from app.db_utils import save_to_db
from langsmith import traceable
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from app.tool_factory import *

API_KEY_GROQ = os.getenv("GROQ_API_KEY")


llm = init_chat_model("llama-3.3-70b-versatile", model_provider="groq")

llm_with_tools = llm.bind_tools(tools)

llm_vision = ChatGroq(
    api_key=API_KEY_GROQ, model="llama-3.2-90b-vision-preview", temperature=0.1
)


@traceable
def route_request(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Route the request to either add or search for expenses based on intent."""

    if image_content or image_url:
        return process_image_request(image_content, image_url)

    return process_text_request(user_input)


@traceable
def process_image_request(image_content: str, image_url: str):
    """Handle image-based expense input."""
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
        }
    ]

    expense_data_unstruct = llm_vision.invoke(input_data)
    expense_data_dict = llm_with_tools.invoke(expense_data_unstruct.content)

    if (
        not expense_data_dict.tool_calls
        or "args" not in expense_data_dict.tool_calls[0]
    ):
        return {"intent": "wrong_receipt", "result": "Please upload a valid receipt."}

    expense_data = expense_data_dict.tool_calls[0]["args"]
    print("Expense Data:", expense_data)

    if "date" not in expense_data or not re.match(
        r"\d{4}-\d{2}-\d{2}", expense_data["date"]
    ):
        expense_data["date"] = datetime.now().strftime("%Y-%m-%d")
    return {"intent": "create_expense", "result": parse_expense_input(expense_data)}


@traceable
def process_text_request(user_input: str):
    """Handle text-based expense input."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    user_input_with_date = (
        f"{user_input}"
        "\n# Current Date:"
        f"{current_date}"
        "\nInstructions:"
        "\n- Week start from Sunday"
        "\n- Weekend is Friday and Saturday"
        "\n- Don't use these instructions, this is only for reference"
        "\n- Also ignore meaningless/irrelevant words for expense"
    )

    intent_response = llm_with_tools.invoke(user_input_with_date)
    print("Intent Response:", intent_response)

    if not intent_response.tool_calls or len(intent_response.tool_calls) == 0:
        return {
            "intent": "unknown",
            "result": "Could not determine intent. Please refine your input.",
        }

    # Process all tool calls returned by the LLM.
    results = []

    for tool_call in intent_response.tool_calls:
        intent = tool_call["name"]
        parsed_input = tool_call["args"]

        print("Intent:", intent)
        print("Parsed Input:", parsed_input)

        if intent == "create_expense":
            result = parse_expense_input(parsed_input)
        elif intent == "greetings":
            result = greetings.invoke({})
        elif intent in [tool.name for tool in tools]:
            result = process_search_request(intent, parsed_input)
        else:
            result = f"Could not determine intent for {intent}. Please try again."

        results.append({"intent": intent, "result": result})

    if len(results) == 1:
        return results[0]
    else:
        results = llm.invoke(
            f"Merge all tool calls into single meaningful response mentioning all tool calls: \n {results} \n"
            "\nInstructions:"
            "\n- Don't use these instructions, this is only for reference"
            "\n- Also ignore meaningless/irrelevant words for expense"
        )
        return {"intent": "multi", "results": results.content}


@traceable
def process_search_request(intent: str, parsed_input: dict):
    """Process a search request and return results."""

    tool_function = next((tool for tool in tools if tool.name == intent), None)

    if not tool_function:
        return f"Invalid intent: {intent}"

    result_response = tool_function.invoke(parsed_input)

    if not result_response:
        return "No results found."

    result = llm.invoke(
        f"Explain concisely in general language: \n {result_response} \n"
        "# Instructions:\n"
        "- amount and category must be mentioned \n"
        "- don't add any instructions to the response \n"
        "- don't add any irrelevant words to the response"
        "- if multiple tools are called, try to merge them into a single response according to the user intent"
    )
    result_content = clean_llm_response(result.content)

    return result_content.strip()


def clean_llm_response(response: str):
    """Remove unwanted XML tags from LLM response."""

    start_idx = response.find("<think>")
    end_idx = response.find("</think>") + len("</think>")

    if start_idx != -1 and end_idx != -1:
        response = response[:start_idx] + response[end_idx:]

    return response


@traceable
def parse_expense_input(expense_data: dict):
    """Parse structured expense data and store it in the database."""

    expense_data.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    expense_data["id"] = uuid.uuid4().hex
    save_to_db(expense_data)

    return expense_data


@traceable
def get_from_pgdb(query: str):
    """Retrieve expense data from the database."""

    return llm_with_tools.invoke(query)
