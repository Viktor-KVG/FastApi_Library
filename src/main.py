from fastapi import FastAPI
from src.routers import general_user

app = FastAPI()

app.include_router(general_user.api_router)