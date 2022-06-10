from fastapi import UploadFile
import os

async def write_file(file: UploadFile):
    print("[*] Saving {} ..".format(file.filename))
    content = await file.read()
    filename = os.path.join("../../models/", file.filename)
    with open(filename, 'wb') as out:
        out.write(content)
    print("[*] Done !")
