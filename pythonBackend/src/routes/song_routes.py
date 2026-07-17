from fastapi import APIRouter, UploadFile, Form

from src.controllers.song_controller import handle_process_audio, handle_add_song

router = APIRouter()

@router.post("/process-audio")
async def process_audio(file: UploadFile):
    return await handle_process_audio(file)

@router.post("/add-song")
async def add_song(file: UploadFile, title: str = Form(...), artist: str = Form(...)):
    return await handle_add_song(file, title, artist)