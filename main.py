from fastapi import FastAPI
from app.routers import expense_router

app = FastAPI()

app.include_router(expense_router)
