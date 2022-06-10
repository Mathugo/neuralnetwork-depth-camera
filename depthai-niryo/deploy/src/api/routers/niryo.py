from fastapi import APIRouter

router = APIRouter()

@router.get("/niryo/position", tags=["niryo"])
def position():
    return {"message": "position"}

@router.post("/niryo/set_position/{position}", tags=["niryo"])
def set_position(position: str):
    return {"set position": position}

@router.post("/niryo/restart", tags=["niryo"])
def restart():
    return {"message": "restart"}