from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI()
app.include_router(router)