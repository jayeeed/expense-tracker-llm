from langchain_groq import ChatGroq
from app.schemas import ExpenseSchema


def process_image_with_model(image_url):

    # Initialize ChatGroq with the specific model
    img = ChatGroq(
        model="llama-3.2-90b-vision-preview", max_tokens=100, temperature=0.0
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
    )

    input_data = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Simply extract data from the image as below format:\n    date: str\n    amount: float\n    category: str\n    description: Optional[str]",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                },
            ],
        },
    ]

    # Process the input using the model
    response = img.invoke(input=input_data)

    llm_response = llm.with_structured_output(ExpenseSchema).invoke(
        input=response.content
    )

    return llm_response


# Example usage
if __name__ == "__main__":
    image_url = "https://templates.invoicehome.com/invoice-template-en-neat-750px.png"
    try:
        response = process_image_with_model(image_url)
        print("Model Response:", response)
    except Exception as e:
        print("An error occurred:", e)
