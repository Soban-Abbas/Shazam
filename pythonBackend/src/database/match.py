from collections import defaultdict, Counter

from src.functions.spectrogram import get_spectrogram
from src.functions.peaks import find_peaks
from src.functions.hashing import generate_hashes
from src.database.connection import get_connection

def match_song(query_audio_path):
    spectrogram_db, sr = get_spectrogram(query_audio_path)
    peaks = find_peaks(spectrogram_db)
    query_hashes = generate_hashes(peaks)

    conn = get_connection()
    cursor = conn.cursor()

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

    if not matches:
        cursor.close()
        conn.close()
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
        cursor.close()
        conn.close()
        return None

    cursor.execute("SELECT title, artist FROM songs WHERE id = %s", (best_song_id,))
    title, artist = cursor.fetchone()
    cursor.close()
    conn.close()

    return {"song": title, "artist": artist, "confidence": best_score}