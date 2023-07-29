from fastapi import FastAPI
from src.restaurant.endpoint import router

app = FastAPI(title="Restaurant")

app.include_router(router)

