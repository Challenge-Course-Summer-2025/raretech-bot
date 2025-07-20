import os
from fastapi import FastAPI
from dotenv import load_dotenv
from api.api import api_router


app = FastAPI()

if os.getenv("ENV") != "production":
    load_dotenv()

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
