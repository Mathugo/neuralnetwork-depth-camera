# app.py
import uvicorn
from fastapi import *
from .routers import models, niryo

app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1",
)

app.include_router(models.router)
app.include_router(niryo.router)

@app.get("/")
def root():
    return {"message": "Hello user"}

@app.on_event("startup")
async def startup():
    """ code here will be run on startup """
    pass 

def start() -> None:
    uvicorn.run("app:app", host="127.0.0.1", port=5000)

if __name__ == "__main__":
    start()