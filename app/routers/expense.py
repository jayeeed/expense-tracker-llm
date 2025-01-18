from app import langchain_utils
from fastapi import APIRouter, File, UploadFile
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
import numpy as np

router = APIRouter()


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess the image for better OCR accuracy."""

    # Convert the PIL Image to a NumPy array
    img_array = np.array(image)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)

    # Apply binary thresholding to get a clean black and white image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Optionally, apply noise reduction (e.g., median blur)
    blurred = cv2.medianBlur(thresh, 1)

    # Optional: Resize to improve OCR accuracy (e.g., double the size)
    height, width = blurred.shape
    new_size = (width * 2, height * 2)
    resized = cv2.resize(blurred, new_size, interpolation=cv2.INTER_CUBIC)

    # Convert back to PIL image
    pil_img = Image.fromarray(resized)
    # Save the preprocessed image to a folder
    output_path = "preprocessed_image.png"
    pil_img.save(output_path)

    return pil_img


@router.post("/handle-expense/")
async def handle_expense(user_input: str = None, file: UploadFile = File(None)):
    """Handle user input to either save or search for expenses."""
    if file:
        try:
            # Read the uploaded image file
            img_bytes = await file.read()
            img = Image.open(BytesIO(img_bytes)).convert("RGBA")

            # Preprocess the image for better OCR results
            preprocessed_img = preprocess_image(img)

            # Extract text from the preprocessed image
            extracted_text = pytesseract.image_to_string(preprocessed_img)
            user_input = extracted_text

        except Exception as e:
            return {"error": f"Failed to process the image: {str(e)}"}

    if not user_input:
        return {"error": "No input provided"}

    result = langchain_utils.route_request(user_input)
    return result
