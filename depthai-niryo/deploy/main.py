#!/usr/bin/python3
import uvicorn, os, asyncio
from fastapi import *
from src.api.routers import models, niryo
from src.app import App
import threading

# Global variables
os.environ["MustStop"] = "False"
APP = None
app_thread = None
API_PORT = 4000
# 400001 --> NIRYO PORT : 4001

""" API """

app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1",
)

""" Router """
app.include_router(models.router)
app.include_router(niryo.router)

""" primary endpoints """

@app.get("/")
def root():
    return {"message": "NiryoOneApi"}

@app.get("/stop")
def stop():
    os.environ["MustStop"] = "True"
    global app_thread
    global APP
    app_thread.join()
    APP.exit()
    return {"message": "App stopped"}

@app.get("/start")
def start():
    os.environ["MustStop"] = "False"
    global app_thread
    app_thread = threading.Thread(target=loop, args=())
    app_thread.start()
    return {"message": "App started"}

### event startup shutdown 

@app.on_event("startup")
async def startup():
    """ code here will run on startup """
    os.environ["MustStop"] = "False"
    global app_thread
    app_thread = threading.Thread(target=loop, args=())
    app_thread.start()
    return {"message": "App started"}

@app.on_event("shutdown")
def shutdown_event():
    """ code here will run on shutdown """
    print("[API] Shutting down the app ..")
    os.environ["MustStop"] = "True"
    global APP
    global app_thread
    app_thread.join()
    APP.exit() 

def loop():
    global APP
    APP = App()
    APP.configure()        
    APP.run()

if __name__ == "__main__":
    # start api then start loop
    print("[API] bind to port {}".format(API_PORT))
    uvicorn.run("main:app", host="0.0.0.0", port=API_PORT)

