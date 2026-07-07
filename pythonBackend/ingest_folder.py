import librosa
import numpy as np
from scipy.ndimage import maximum_filter
import hashlib
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()



conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)


cursor = conn.cursor()

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

def ingest_song(audio_path, title, artist):
    print(f"Processing: {title} by {artist}...")

    spectrogram_db, sr = get_spectrogram(audio_path)
    peaks = find_peaks(spectrogram_db)
    hashes = generate_hashes(peaks)

    cursor.execute(
        "INSERT INTO songs (title, artist) VALUES (%s, %s) RETURNING id",
        (title, artist)
    )
    song_id = cursor.fetchone()[0]

    data_to_insert = [(h, song_id, int(anchor_time)) for h, anchor_time in hashes]
    cursor.executemany(
        "INSERT INTO fingerprints (hash, song_id, anchor_time) VALUES (%s, %s, %s)",
        data_to_insert
    )

    conn.commit()
    print(f"✅ '{title}' ingested with {len(hashes)} fingerprints (song_id: {song_id})\n")


if __name__ == "__main__":
    songs_folder = "songs"

    for filename in os.listdir(songs_folder):
        if filename.endswith(".mp3"):
            file_path = os.path.join(songs_folder, filename)
            # Filename se hi title bana rahe hain (song1.mp3 -> "song1")
            title = os.path.splitext(filename)[0]
            ingest_song(file_path, title=title, artist="Unknown Artist")

    cursor.close()
    conn.close()
    print("All songs ingested!")