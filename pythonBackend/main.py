from fastapi import FastAPI, UploadFile
import shutil
import os
import librosa
import numpy as np
from scipy.ndimage import maximum_filter
import hashlib
import psycopg2
from collections import defaultdict, Counter
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

os.makedirs("received_audio", exist_ok=True)

# ============================
# DATABASE CONNECTION
# ============================
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# ============================
# Spectrogram + Peaks + Hashing (same functions)
# ============================
def get_spectrogram(audio_path):
    y, sr = librosa.load(audio_path)
    D = librosa.stft(y)
    spectrogram = np.abs(D)
    spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)
    return spectrogram_db, sr

def find_peaks(spectrogram_db, neighborhood_size=20):
    neighborhood = maximum_filter(spectrogram_db, size=neighborhood_size) == spectrogram_db
    threshold = np.median(spectrogram_db) + 10
    detected_peaks = neighborhood & (spectrogram_db > threshold)
    freq_idx, time_idx = np.where(detected_peaks)
    peaks = list(zip(time_idx, freq_idx))
    peaks.sort(key=lambda p: p[0])
    return peaks

FAN_VALUE = 5
MIN_TIME_DELTA = 0
MAX_TIME_DELTA = 200

def generate_hashes(peaks, fan_value=FAN_VALUE):
    hashes = []
    for i in range(len(peaks)):
        anchor_time, anchor_freq = peaks[i]
        for j in range(1, fan_value + 1):
            if (i + j) < len(peaks):
                target_time, target_freq = peaks[i + j]
                time_delta = target_time - anchor_time
                if MIN_TIME_DELTA <= time_delta <= MAX_TIME_DELTA:
                    hash_input = f"{anchor_freq}|{target_freq}|{time_delta}"
                    h = hashlib.sha1(hash_input.encode()).hexdigest()[0:20]
                    hashes.append((h, int(anchor_time)))
    return hashes

# ============================
# MATCHING LOGIC
# ============================
def match_song(query_audio_path):
    conn = get_connection()
    cursor = conn.cursor()

    spectrogram_db, sr = get_spectrogram(query_audio_path)
    peaks = find_peaks(spectrogram_db)
    query_hashes = generate_hashes(peaks)

    matches = defaultdict(list)

    for h, query_time in query_hashes:
        cursor.execute(
            "SELECT song_id, anchor_time FROM fingerprints WHERE hash = %s",
            (h,)
        )
        results = cursor.fetchall()

        for song_id, db_anchor_time in results:
            delta = db_anchor_time - query_time
            matches[song_id].append(delta)

    cursor.close()
    conn.close()

    if not matches:
        return None

    best_song_id = None
    best_score = 0

    for song_id, deltas in matches.items():
        delta_counts = Counter(deltas)
        most_common_delta, count = delta_counts.most_common(1)[0]

        if count > best_score:
            best_score = count
            best_song_id = song_id

    if best_song_id is None:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, artist FROM songs WHERE id = %s", (best_song_id,))
    title, artist = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"song": title, "artist": artist, "confidence": best_score}


# ============================
# API ROUTE
# ============================
@app.post("/process-audio")
async def process_audio(file: UploadFile):
    save_path = f"received_audio/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = match_song(save_path)

    if result is None:
        return {"song": None, "artist": None, "message": "No match found"}

    return result