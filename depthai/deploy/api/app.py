# app.py
import uvicorn
from fastapi import *

app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1",
)

@app.get("/")
def home():
    return {"message": "hello world"}

async def start() -> None:
    uvicorn.run("api:app", host="127.0.0.1", port=5000)

if __name__ == "__main__":
    start()