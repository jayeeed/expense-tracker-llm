from app import langchain_utils
from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter()


@router.post("/handle-expense/")
async def handle_expense(
    user_input: str = Form(None),
    image: UploadFile = File(None),
    image_url: str = Form(None),
):
    """Handle user input to either save or search for expenses, with optional image or image URL."""
    if user_input:
        result = langchain_utils.parse_expense_input(user_input)
    elif image:
        image_content = await image.read()
        result = langchain_utils.route_request(image_content)
    # elif image_url:
    #     result = langchain_utils.parse_expense_input(image_url)
    else:
        result = {"error": "No input provided"}

    return result
