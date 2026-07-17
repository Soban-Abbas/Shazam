import shutil
import os
from pydub import AudioSegment

from src.database.ingest import ingest_song
from src.database.match import match_song

os.makedirs("received_audio", exist_ok=True)
os.makedirs("songs", exist_ok=True)


async def handle_process_audio(file):
    temp_path = f"received_audio/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    wav_path = temp_path.rsplit(".", 1)[0] + ".wav"
    audio = AudioSegment.from_file(temp_path)
    audio.export(wav_path, format="wav")

    result = match_song(wav_path)

    if result is None:
        return {"song": None, "artist": None, "message": "No match found"}
    return result


async def handle_add_song(file, title, artist):
    save_path = f"songs/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_song(save_path, title=title, artist=artist)

    return {"message": f"'{title}' by {artist} added successfully"}