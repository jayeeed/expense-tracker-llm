from app import langchain_utils
from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter()


@router.post("/handle-expense/")
async def handle_expense(user_input: str = Form(None), image: UploadFile = File(None)):
    """Handle user input to either save or search for expenses, with optional image."""
    if user_input:
        # Handle text input
        result = langchain_utils.route_request(user_input)
    elif image:
        # # If there's an image, process it using the llm_vision model
        # image_content = await image.read()
        result = langchain_utils.route_request(image)  # Process image
    else:
        result = {"error": "No input provided"}

    return result
