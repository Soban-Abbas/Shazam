import librosa
import numpy as np
from scipy.ndimage import maximum_filter
import hashlib
import psycopg2

# ============================
# DATABASE CONNECTION
# ============================
conn = psycopg2.connect(
    dbname="shazam_db",
    user="postgres",
    password="soban2669",   
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ============================
# STEP 1: Audio Load + Spectrogram
# ============================
def get_spectrogram(audio_path):
    y, sr = librosa.load(audio_path)
    D = librosa.stft(y)
    spectrogram = np.abs(D)
    spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)
    return spectrogram_db, sr

# ============================
# STEP 2: Peak Detection
# ============================
def find_peaks(spectrogram_db, neighborhood_size=20):
    neighborhood = maximum_filter(spectrogram_db, size=neighborhood_size) == spectrogram_db
    threshold = np.median(spectrogram_db) + 10
    detected_peaks = neighborhood & (spectrogram_db > threshold)
    freq_idx, time_idx = np.where(detected_peaks)
    peaks = list(zip(time_idx, freq_idx))
    peaks.sort(key=lambda p: p[0])
    return peaks

# ============================
# STEP 3: Hash Generation
# ============================
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
                    hashes.append((h, anchor_time))
    return hashes

# ============================
# STEP 4: Database Insert
# ============================
def ingest_song(audio_path, title, artist):
    print(f"Processing: {title} by {artist}...")

    # Spectrogram + Peaks + Hashes
    spectrogram_db, sr = get_spectrogram(audio_path)
    peaks = find_peaks(spectrogram_db)
    hashes = generate_hashes(peaks)

    print(f"Peaks found: {len(peaks)}, Hashes generated: {len(hashes)}")

    # Pehle songs table mein entry daalo, song_id lo
    cursor.execute(
        "INSERT INTO songs (title, artist) VALUES (%s, %s) RETURNING id",
        (title, artist)
    )
    song_id = cursor.fetchone()[0]

    # Ab saare hashes fingerprints table mein daalo (bulk insert - fast)
    # data_to_insert = [(h, song_id, anchor_time) for h, anchor_time in hashes]
    # data_to_insert = [(h, song_id, int(anchor_time)) for h, anchor_time in hashes]
    data_to_insert = [(h, song_id, int(anchor_time)) for h, anchor_time in hashes]
    cursor.executemany(
        "INSERT INTO fingerprints (hash, song_id, anchor_time) VALUES (%s, %s, %s)",
        data_to_insert
    )

    conn.commit()
    print(f"✅ '{title}' ingested successfully with {len(hashes)} fingerprints (song_id: {song_id})\n")


# ============================
# RUN — Apna test.mp3 ingest karo
# ============================
if __name__ == "__main__":
    ingest_song("test.mp3", title="Test Song", artist="Test Artist")

    cursor.close()
    conn.close()