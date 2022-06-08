from app import *
#from fastapi import FastAPI, File, UploadFile

@app.get("/model")
def get_model():
    # code to return some fruits
    return {"message": "some models"}

from model.upload_model import *
from model.set_model import *
from model.list_model import *