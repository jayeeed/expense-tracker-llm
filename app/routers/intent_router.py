from app.langchain_utils import (
    llm,
    parse_expense_input,
    get_from_vectordb,
    get_from_pgdb,
)
from app.schemas import IntentDetection


def route_request(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Route the request to either add or search for expenses based on intent."""

    if image_content or image_url:
        return {
            "intent": "add_expense",
            "result": parse_expense_input(
                image_content=image_content, image_url=image_url
            ),
        }

    intent_response = llm.with_structured_output(IntentDetection).invoke(user_input)
    intent = intent_response["intent"].strip()

    print("intent detected: ", intent)

    if intent == "add_expense":
        result = parse_expense_input(user_input=user_input)
    elif intent == "search_expense":
        # result = get_from_vectordb(user_input=user_input)
        result = get_from_pgdb(user_input=user_input)
    else:
        result = {"error": "Could not determine intent. Please try again."}

    return {"intent": intent, "result": result}
