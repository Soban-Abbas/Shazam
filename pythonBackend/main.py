from fastapi import FastAPI, UploadFile
import shutil
import os

app = FastAPI()

os.makedirs("received_audio", exist_ok=True)

@app.post("/process-audio")
async def process_audio(file: UploadFile):
    save_path = f"received_audio/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "song": "Test Song",
        "artist": "Test Artist"
    }