import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import ngrok
import uvicorn
from app.routers import expense_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expense_router)

# custom_domain = os.getenv("NGROK_URL", "intense-secondly-gecko.ngrok-free.app")
# public_url = ngrok.connect(addr=8000, url=custom_domain)

# print(f"Public URL: {public_url}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)
