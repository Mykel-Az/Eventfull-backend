from fastapi import UploadFile
import shutil
import os



UPLOAD_DIRECTORY = "events_uploaded_file"

def save_to_file(file: UploadFile, directory: str):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file.filename




