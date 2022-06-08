from app import app

@app.post("/niryo/restart")
def set_position():
    return {"message": "restart"}