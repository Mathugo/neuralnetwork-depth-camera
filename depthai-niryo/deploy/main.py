#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Robotic Solution for NiryoOne and OAK-D Camera.

This python script demonstrates the whole program functions which is :
    * Run a depthai object detection model 
    * Control the niryo and give him position of interest to grab detected objects
    * Expose a restapi capable of displaying results, niryo's position and managing the app
    * Send results to the selected mosquitto broker on diferents channels

This program is run via docker using *build_run.sh* bash script. In this case you have 
to replace some of the given parameters in *build_run.sh*. This bash script will build and run the image 
but if you want to just pull the image and run it you can use the argument ``sudo bash build_run.sh --run``

You can also run it using a python interpreter with 3.9>python_version>=3.5 and 
install the requirements in *requirements.txt* via ``python -m pip install -r requirements.txt``

Attributes:
    MQTT_BROKER (str)      : Ip address of the MQTT Broker 
    MQTT_PORT (str)        : Port of the MQTT Broker
    MQTT_CAM_TOPIC (str)   : MQTT Topic where the camera's results will be send (objects position ..)
    MQTT_NIRYO_TOPIC (str) : MQTT Topic where the niryo's results will be send (position ..)
    MODEL            (str) : Depthai blob model located directly in /depthai-niryo/deploy/models
    CONFIG           (str) : Depthai json config is mandatory to run blob model, located in /depthai-niryo/deploy/config
    ps: Additionals parameters to increase accuracy and speed can be find in *src/app/app.py*

Examples:
    Docker:
        $ sudo chmod +x build_run.sh
        $ sudo bash build_run.sh

    Python interpeter:
        $ sudo python3 main.py --model <model.blob> --config <config.json> \
        --mqtt_broker <localhost> --mqtt_cam_topic <cam> --mqtt_niryo_topic <niryo> 
"""

from sys import path
path.append("/app/build/python_tcp_client")
path.append("/app/models/")
path.append("/app/config/")
"""Append source code to access it"""

import uvicorn, os, threading
from fastapi import *
from src.api.routers import models, niryo
from src.app import App
from src.utils import global_var
"""Import source code"""

"""API"""
app = FastAPI(
    title="Orange Rest API for depthai and niryo",
    description=""" Manage models and niryo robot from the api""",
    version="0.0.1")

"""Router """
app.include_router(models.router)
app.include_router(niryo.router)

"""Primary endpoints """
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

"""API event"""
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

"""Main program loop"""
def loop():
    global_var.APP = App()
    global_var.APP.configure()        
    global_var.APP.run()

if __name__ == "__main__":
    # start api then start loop
    global_var.init_var()
    print("[API] bind to port {}".format(global_var.API_PORT))
    uvicorn.run("main:app", host="0.0.0.0", port=global_var.API_PORT)

