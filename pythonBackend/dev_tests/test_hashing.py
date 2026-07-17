import librosa
import numpy as np
from scipy.ndimage import maximum_filter
import hashlib

audio_path = "test.mp3"
y, sr = librosa.load(audio_path)

D = librosa.stft(y)
spectrogram = np.abs(D)
spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)

def find_peaks(spectrogram_db, neighborhood_size=20):
    neighborhood = maximum_filter(spectrogram_db, size=neighborhood_size) == spectrogram_db
    threshold = np.median(spectrogram_db) + 10
    detected_peaks = neighborhood & (spectrogram_db > threshold)
    freq_idx, time_idx = np.where(detected_peaks)
    return freq_idx, time_idx

freq_idx, time_idx = find_peaks(spectrogram_db)

# Peaks ko (time, frequency) pairs mein organize karo, time ke hisaab se sort karo
peaks = list(zip(time_idx, freq_idx))
peaks.sort(key=lambda p: p[0])  # time ke hisaab se sort

print(f"Total peaks: {len(peaks)}")

# ============================
# HASHING - Anchor + Target Zone
# ============================

FAN_VALUE = 5          # har anchor ko kitne target peaks ke sath pair karna hai
MIN_TIME_DELTA = 0     # target peaks ka minimum time gap anchor se
MAX_TIME_DELTA = 200   # target peaks ka maximum time gap anchor se (frames mein)

def generate_hashes(peaks, fan_value=FAN_VALUE):
    hashes = []

    for i in range(len(peaks)):
        anchor_time, anchor_freq = peaks[i]

        # Anchor ke baad ke kuch peaks ko target banate hain (target zone)
        for j in range(1, fan_value + 1):
            if (i + j) < len(peaks):
                target_time, target_freq = peaks[i + j]

                time_delta = target_time - anchor_time

                if MIN_TIME_DELTA <= time_delta <= MAX_TIME_DELTA:
                    # Teen values se ek unique string banao: freq1, freq2, time_delta
                    hash_input = f"{anchor_freq}|{target_freq}|{time_delta}"

                    # Isko ek chota hash code (SHA1) mein convert karo
                    h = hashlib.sha1(hash_input.encode()).hexdigest()[0:20]

                    # Hash ke sath anchor ka absolute time bhi save karo
                    hashes.append((h, anchor_time))

    return hashes

hashes = generate_hashes(peaks)

print(f"Total hashes generated: {len(hashes)}")

print("\nFirst 10 hashes (hash, anchor_time_frame):")
for i in range(min(10, len(hashes))):
    print(hashes[i])