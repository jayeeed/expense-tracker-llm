import base64
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, File, UploadFile, Form
from app.langchain_utils import route_request

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


async def process_image(image_file: UploadFile, max_size: tuple = (800, 800)) -> str:
    """Resize image to fit within max_size and convert to base64."""
    image = Image.open(BytesIO(await image_file.read()))

    # Convert to RGB if necessary (to handle PNGs with transparency)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Resize while maintaining aspect ratio
    image.thumbnail(max_size)

    # Save to bytes and encode to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


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
        image_content = await process_image(image_file)
        result = route_request(image_content=image_content)
    elif image_url:
        result = route_request(image_url=image_url)
    else:
        result = {"error": "No input provided"}

    return result
