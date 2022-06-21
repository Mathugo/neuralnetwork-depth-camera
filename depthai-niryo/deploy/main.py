#!/usr/bin/python3
import uvicorn, os, threading, sys
sys.path.append("/app/build/python_tcp_client")
sys.path.append("/app/models/")
sys.path.append("/app/config/")
from fastapi import *
from src.api.routers import models, niryo
from src.app import App
from src.utils import global_var

""" API """
app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1")

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
    global_var.app_thread.join()
    APP.exit()
    return {"message": "App stopped"}

@app.get("/start")
def start():
    os.environ["MustStop"] = "False"
    global_var.app_thread = threading.Thread(target=loop, args=())
    global_var.app_thread.start()
    return {"message": "App started"}

### event startup shutdown 

@app.on_event("startup")
async def startup():
    """ code here will run on startup """
    os.environ["MustStop"] = "False"
    global_var.app_thread = threading.Thread(target=loop, args=())
    global_var.app_thread.start()
    return {"message": "App started"}

@app.on_event("shutdown")
def shutdown_event():
    """ code here will run on shutdown """
    print("[API] Shutting down the app ..")
    os.environ["MustStop"] = "True"
    global_var.app_thread.join()
    global_var.APP.exit() 

def loop():
    global_var.APP = App()
    global_var.APP.configure()        
    global_var.APP.run()

if __name__ == "__main__":
    # start api then start loop
    global_var.init_var()
    print("[API] bind to port {}".format(global_var.API_PORT))
    uvicorn.run("main:app", host="0.0.0.0", port=global_var.API_PORT)

