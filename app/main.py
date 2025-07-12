from fastapi import FastAPI
from dotenv import load_dotenv
import os

app = FastAPI()

if os.getenv("ENV") != "production":
    load_dotenv()  # .env を読み込む

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}