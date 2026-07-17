from fastapi import FastAPI
import os

from src.routes.song_routes import router

os.environ["PATH"] += os.pathsep + r"C:\Users\soban\Downloads\ffmpeg-8.1.2-essentials_build\ffmpeg-8.1.2-essentials_build\bin"

app = FastAPI()

app.include_router(router)