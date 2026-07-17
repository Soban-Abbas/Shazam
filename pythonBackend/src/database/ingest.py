from src.functions.spectrogram import get_spectrogram
from src.functions.peaks import find_peaks
from src.functions.hashing import generate_hashes
from src.database.connection import get_connection

def ingest_song(audio_path, title, artist):
    spectrogram_db, sr = get_spectrogram(audio_path)
    peaks = find_peaks(spectrogram_db)
    hashes = generate_hashes(peaks)

    conn = get_connection()
    cursor = conn.cursor()

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
    cursor.close()
    conn.close()
    print(f"'{title}' ingested with {len(hashes)} fingerprints")