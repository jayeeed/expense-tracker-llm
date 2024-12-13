from datetime import datetime
from langchain_ollama import ChatOllama
from .schemas import ExpenseCreate, ExpenseQuerySchema

llm = ChatOllama(model="llama3.2:1b")

structured_llm = llm.with_structured_output(ExpenseCreate)
structured_query_llm = llm.with_structured_output(ExpenseQuerySchema)


def parse_expense_input(user_input: str) -> ExpenseCreate:
    response = structured_llm.invoke(user_input)

    if not response.log_date:
        response.log_date = datetime.now().date().strftime("%Y-%m-%d")

    return response


def parse_query_input(user_input: str) -> ExpenseQuerySchema:
    try:
        response = structured_query_llm.invoke(user_input)
        return response
    except Exception as e:
        print(f"Error parsing input: {e}")
        return ExpenseQuerySchema()
