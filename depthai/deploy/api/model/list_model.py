from app import app

@app.get("/model/list")
def list_model():
    return {"message": "model"}