import librosa
import numpy as np
from scipy.ndimage import maximum_filter, generate_binary_structure, binary_erosion
import matplotlib.pyplot as plt
import librosa.display

# Step 1: Audio load karo (jaisa pehle kiya tha)
audio_path = "test.mp3"
y, sr = librosa.load(audio_path)

# Step 2: Spectrogram banao
D = librosa.stft(y)
spectrogram = np.abs(D)
spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)

# Step 3: Peaks nikalo (local maxima dhundo)
# Ye function har point ko check karta hai: "kya ye apne aas paas ke sab points se loud hai?"
def find_peaks(spectrogram_db, neighborhood_size=20):
    # Ek "structure" banate hain jo batata hai kitne neighbors check karne hain
    struct = generate_binary_structure(2, 1)
    neighborhood = maximum_filter(spectrogram_db, size=neighborhood_size) == spectrogram_db

    # Bohot quiet points ko peak nahi maanenge (background noise ho sakta hai)
    threshold = np.median(spectrogram_db) + 10
    detected_peaks = neighborhood & (spectrogram_db > threshold)

    # Peaks ke coordinates nikalo (frequency index, time index)
    freq_idx, time_idx = np.where(detected_peaks)
    return freq_idx, time_idx

freq_idx, time_idx = find_peaks(spectrogram_db)

print(f"Total peaks found: {len(freq_idx)}")

# Step 4: Peaks ko actual time (seconds) aur frequency (Hz) mein convert karo
times = librosa.frames_to_time(time_idx, sr=sr)
freqs = librosa.fft_frequencies(sr=sr)[freq_idx]

# Pehle 10 peaks print karo dekhne ke liye
print("\nFirst 10 peaks (time, frequency):")
for i in range(min(10, len(times))):
    print(f"Time: {times[i]:.2f}s, Frequency: {freqs[i]:.2f}Hz")

# Step 5: Spectrogram pe peaks ko plot karo (visually dekhne ke liye)
plt.figure(figsize=(12, 6))
librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.scatter(times, freqs, color='red', s=10, marker='x')
plt.title(f'Spectrogram with {len(freq_idx)} Peaks Detected')
plt.savefig('peaks_output.png')
print("\nPeaks image saved as 'peaks_output.png'")