#!/usr/bin/python3
import uvicorn
from fastapi import *
import asyncio
from src.api.routers import models, niryo
from src.app import App

# Global variables
mustStop = False

app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1",
)

app.include_router(models.router)
app.include_router(niryo.router)

@app.get("/stop")
def stop():
    global mustStop
    mustStop = True
    return {"message": "App stopped"}

@app.get("/start")
def start():
    global mustStop
    mustStop = False
    loop()

@app.on_event("startup")
async def startup():
    """ code here will be run on startup """
    loop()

def loop():
    APP = App()
    APP.configure()        
    APP.run()

if __name__ == "__main__":
    # start api then start loop
    uvicorn.run("main:app", host="127.0.0.1", port=5000)
