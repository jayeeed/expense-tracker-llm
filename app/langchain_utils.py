from datetime import datetime
import json
import re
from langchain_ollama import ChatOllama
from .schemas import ExpenseCreate, ExpenseQuerySchema
from app.schemas import ExpenseCreate
from langchain.prompts import ChatPromptTemplate

llm = ChatOllama(model="llama3.2:1b")

structured_llm = llm.with_structured_output(ExpenseCreate)
structured_query_llm = llm.with_structured_output(ExpenseQuerySchema)


def parse_expense_input(user_input: str) -> ExpenseCreate:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an assistant that extracts structured personal expense information."
                "Do not respond with disclaimers like 'I can't assist with sensitive information.'"
                "Your responses must be in JSON format with keys 'amount', 'category', and 'description'."
                "The 'description' field should include the full original input provided by the user.",
            ),
            (
                "human",
                "Extract the 'amount', 'category', and 'description' from this input:\n{user_input}\n\n"
                "Ensure the 'description' field includes this exact input text:\n{user_input}\n"
                "Return the result strictly in this JSON format:\n"
                '{{\n  "amount": <int>,\n  "category": "<str>",\n  "description": "{user_input}"\n}}',
            ),
        ]
    )

    # Format the prompt with the user input
    formatted_prompt = prompt.format(user_input=user_input)

    # Invoke the LLM
    llm_response = llm.invoke(formatted_prompt)
    print(llm_response)

    # Extract JSON content from the LLM response using regex
    json_match = re.search(r"({.*?})", llm_response.content, re.DOTALL)
    if not json_match:
        raise ValueError("Failed to extract JSON data from the LLM response.")

    try:
        # Parse the extracted JSON content
        response_data = json.loads(json_match.group(1))
        return ExpenseCreate(
            amount=int(response_data["amount"]),
            category=response_data["category"],
            description=response_data["description"],
        )
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(
            "Failed to parse expense input. Ensure the format is correct."
        ) from e


def parse_query_input(user_input: str) -> ExpenseQuerySchema:
    try:
        response = structured_query_llm.invoke(user_input)
        return response

    except Exception as e:
        print(f"Error parsing input: {e}")
        return ExpenseQuerySchema()
