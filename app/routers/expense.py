from app import langchain_utils
from fastapi import APIRouter, File, UploadFile, Form
from fastapi import HTTPException
import requests
from io import BytesIO
from PIL import Image

router = APIRouter()


@router.post("/handle-expense/")
async def handle_expense(
    user_input: str = Form(None),
    image: UploadFile = File(None),
    image_url: str = Form(None),
):
    """Handle user input to either save or search for expenses, with optional image or image URL."""
    if user_input:
        # Handle text input
        result = langchain_utils.route_request(user_input)
    elif image:
        # If there's an image, process it using the llm_vision model
        image_content = await image.read()
        result = langchain_utils.route_request(image_content)  # Process image
    elif image_url:
        # If there's an image URL, download and process it
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            print(response)
            # image_content = BytesIO(response.content)
            # image = Image.open(image_content)
            result = langchain_utils.route_request(image_url)
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=400, detail=f"Error fetching image from URL: {e}"
            )
    else:
        result = {"error": "No input provided"}

    return result
