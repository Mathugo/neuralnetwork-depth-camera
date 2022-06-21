from fastapi import UploadFile, APIRouter
from ..utils import write_file
import os

router = APIRouter()

@router.get("/models", tags=["models"])
async def models():
    return {"message": os.listdir("models")}

@router.post("/models/upload", tags=["models"])
async def upload_model(file: UploadFile):
    if not file:
        return {"message": "no file sent"}
    else:
        await write_file(file)
        return {"Uploaded filename": file.filename}
