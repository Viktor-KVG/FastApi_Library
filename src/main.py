from fastapi import FastAPI

from src.routers import general_user, general_author

app = FastAPI()

app.include_router(general_user.api_router)
app.include_router(general_author.api_router)