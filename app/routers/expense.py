import base64
from app.routers.intent_router import route_request
from fastapi import APIRouter, File, UploadFile, Form

router = APIRouter()


@router.post("/handle-expense/")
async def handle_expense(
    user_input: str = Form(None),
    image_file: UploadFile = File(None),
    image_url: str = Form(None),
):
    """Handle user input to either save or search for expenses, with optional image or image URL."""
    if user_input:
        result = route_request(user_input=user_input)
    elif image_file:
        image_content = base64.b64encode(await image_file.read()).decode("utf-8")
        result = route_request(image_content=image_content)
    elif image_url:
        result = route_request(image_url=image_url)
    else:
        result = {"error": "No input provided"}

    return result
