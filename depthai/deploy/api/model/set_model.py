from app import app

@app.post("/model/set")
def set_model():
    return {"message": "Test"}