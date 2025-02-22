import streamlit as st
import base64
import json
from io import BytesIO
from PIL import Image
from app.langchain_utils import route_request
from dotenv import load_dotenv

load_dotenv()


def process_image(image_file, max_size=(800, 800)):
    """Resize image to fit within max_size and convert to base64."""
    image = Image.open(image_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("L")
    image.thumbnail(max_size)
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Initialize conversation history in session_state
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Expense Analyzer")
st.write("Chat with me to process your expense receipts.")

# Allow the user to upload an image
uploaded_file = st.file_uploader(
    "Upload a receipt image to add expenses",
    type=["jpg", "jpeg", "png"],
    key="image_upload",
)

# If an image is uploaded, display it in the chat as a user message
if uploaded_file:
    st.chat_message("user").image(Image.open(uploaded_file), caption="Uploaded Image")

# Chat input box for user text
user_message = st.chat_input("Type your message here...")

if user_message:
    # Save the user message to the session state
    st.session_state["messages"].append({"role": "user", "message": user_message})

    # Process the image if one was uploaded
    image_content = process_image(uploaded_file) if uploaded_file else None

    # Get the assistant response by calling route_request
    response = route_request(user_input=user_message, image_content=image_content)

    # Attempt to extract the "result" field or check for "id" in the response if it's JSON-like
    try:
        if isinstance(response, dict):
            if "id" in response:
                result_text = "Record added successfully"
            else:
                result_text = response.get("result", response)
        else:
            parsed = json.loads(response)
            if "id" in parsed:
                result_text = "Record added successfully"
            else:
                result_text = parsed.get("result", response)
    except Exception:
        result_text = response

    st.session_state["messages"].append({"role": "assistant", "message": result_text})

    # Force rerun to clear the file uploader after submission
    st.rerun()

# Render the conversation history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["message"])
    else:
        st.chat_message("assistant").write(msg["message"])
