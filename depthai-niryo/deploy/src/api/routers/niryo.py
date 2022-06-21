from fastapi import APIRouter
from pydantic import BaseModel
from src.utils import global_var
from src.niryo import Niryo

router = APIRouter()

@router.get("/niryo/position", tags=["niryo"])
def position():
    pos = global_var.NIRYO.position if global_var.NIRYO != None else "None"
    return {"message": pos}

@router.post("/niryo/increment_pos/{axis}/{pos}", tags=["niryo"])
async def increment_pos(axis: str, pos: float):
    await global_var.NIRYO.increment_pos(axis, pos)
    return {"message": "position of {} incremented by {}".format(axis, pos)}

@router.post("/niryo/move_to_roi/{position}", tags=["niryo"])
async def move_to_roi(position: str):
    print("Position wanted : "+position)
    _roi = position.split(",")
    try:
        x = float(_roi[0])
        y = float(_roi[1])
        z = float(_roi[2])
        print('X {} Y {} Z {}'.format(x,y,z))
        await global_var.NIRYO.move_to_roi(x, y, z)
        return {"message": "niryo moved to ({},{},{})".format(x,y,z)}
    except:
        return {"set position": "error {} not a valid position, see /niryo/move_to_roi/help"}

@router.get("/niryo/move_to_roi/help", tags=["niryo"])
def move_to_roi_help(): 
    return {"help move_to_roi": "{x,y,z} --> move to roi"}

@router.get("/niryo/stop", tags=["niryo"])
async def stop():
    global_var.NIRYO.quit()
    global_var.NIRYO = None
    return {"message": "niryo stopped"}

@router.get("/niryo/start", tags=["niryo"])
async def start():
    global_var.NIRYO = Niryo()
    return {"message": "niryo started"}

@router.get("/niryo/restart", tags=["niryo"])
async def restart():
    if global_var.NIRYO != None: global_var.NIRYO.quit()
    global_var.NIRYO = Niryo()
    return {"message": "niryo restarted"}