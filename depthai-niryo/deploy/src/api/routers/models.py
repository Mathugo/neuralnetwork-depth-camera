# -*- coding: utf-8 -*-
"""FastAPI models endpoints"""

from fastapi import UploadFile, APIRouter
from ..utils import write_file
import os

router = APIRouter()

@router.get("/models", tags=["models"])
async def models():
    """List all the models located in /models folder"""
    return {"message": os.listdir("models")}

@router.post("/models/upload", tags=["models"])
async def upload_model(file: UploadFile):
    """Upload desired model to /models folder"""
    if not file:
        return {"message": "no file sent"}
    else:
        await write_file(file)
        return {"Uploaded filename": file.filename}
