from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import expense_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(expense_router)
