from app import app

@app.get("/niryo/position")
def position():
    return {"message": "position"}

@app.post("/niryo/set_position")
def set_position():
    return {"message": "set position"}

