# -*- coding: utf-8 -*-
"""FastAPI niryo endpoints"""

from fastapi import APIRouter
from pydantic import BaseModel
from src.utils import global_var
from src.niryo import Niryo

router = APIRouter()

@router.get("/niryo/position", tags=["niryo"])
def position():
    """Get the 6 relative position from the niryo"""
    pos = global_var.NIRYO.position if global_var.NIRYO != None else "None"
    return {"message": pos}

@router.post("/niryo/increment_pos/{axis}/{pos}", tags=["niryo"])
def increment_pos(axis: str, pos: float):
    """Increment one specific position, ex : 0.1 meter in x"""
    global_var.NIRYO.increment_pos(axis, pos)
    return {"message": "position of {} incremented by {}".format(axis, pos)}

@router.get("/niryo/open_gripper", tags=["niryo"])
def open_gripper():
    """Open the niryo's gripper"""
    if global_var.NIRYO != None:
        global_var.NIRYO.open_gripper(global_var.NIRYO.grip, 500)
        return {"message": "gripper openned !"}
    else:
        return {"message": "niryo not currently alive"}

@router.get("/niryo/close_gripper", tags=["niryo"])
def close_gripper():
    """Close the niryo's gripper"""
    if global_var.NIRYO != None:
        global_var.NIRYO.close_gripper(global_var.NIRYO.grip, 500)
        return {"message": "gripper closed !"}
    else:
        return {"message": "niryo not currently alive"}

@router.get("/niryo/stop", tags=["niryo"])
async def stop():
    """Stop the niryo by shutting down the tcp server"""
    if global_var.NIRYO != None:
        global_var.NIRYO.quit()
        global_var.NIRYO = None
        return {"message": "niryo stopped"}
    else:
        return {"message": "niryo already stopped"}

@router.get("/niryo/start", tags=["niryo"])
async def start():
    """Start the niryo (connect to the server, calibrate and go to stand by position"""
    if global_var.NIRYO == None:
        global_var.NIRYO = Niryo()
        return {"message": "niryo started"}
    else:
        return {"message": "niryo already started"}

@router.get("/niryo/restart", tags=["niryo"])
async def restart():
    """Restart niryo object"""
    if global_var.NIRYO != None: global_var.NIRYO.quit()
    global_var.NIRYO = Niryo()
    return {"message": "niryo restarted"}