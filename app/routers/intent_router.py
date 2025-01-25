from app.langchain_utils import (
    llm,
    parse_expense_input,
    get_from_vectordb,
    get_from_pgdb,
)

INTENT_OPTIONS = ["add_expense", "search_expense", "unknown"]


def route_request(
    user_input: str = None, image_content: str = None, image_url: str = None
):
    """Route the request to either add or search for expenses based on intent."""

    if image_content or image_url:
        return parse_expense_input(image_content=image_content, image_url=image_url)

    intent_detection_prompt = (
        "You are an intent detection model. Classify the following input as one of these options:\n"
        f"{', '.join(INTENT_OPTIONS)}.\n"
        f"Input: {user_input}\n"
        "Output:"
    )

    intent_response = llm.invoke(intent_detection_prompt).content.strip().lower()
    intent = intent_response if intent_response in INTENT_OPTIONS else "unknown"

    print("intent detected: ", intent)

    if intent == "add_expense":
        result = parse_expense_input(user_input=user_input)
    elif intent == "search_expense":
        # result = get_from_vectordb(user_input=user_input)
        result = get_from_pgdb(user_input=user_input)
    else:
        result = {"error": "Could not determine intent. Please try again."}

    return {"intent": intent, "result": result}
