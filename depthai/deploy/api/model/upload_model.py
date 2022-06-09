from app import app
from fastapi import UploadFile

@app.post("/model/upload")
async def upload_model(file: UploadFile):
    return {"filename": file.filename}
