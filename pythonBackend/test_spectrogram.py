import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Audio file load karo
audio_path = "test.mp3"
y, sr = librosa.load(audio_path)

print(f"Audio loaded successfully!")
print(f"Sample rate: {sr}")
print(f"Duration: {len(y)/sr:.2f} seconds")

# Step 2: Spectrogram banao (STFT - Short Time Fourier Transform)
D = librosa.stft(y)
spectrogram = np.abs(D)

print(f"Spectrogram shape: {spectrogram.shape}")

# Step 3: Spectrogram ko dB scale mein convert karo (dekhne ke liye behtar hota hai)
spectrogram_db = librosa.amplitude_to_db(spectrogram, ref=np.max)

# Step 4: Plot karo (image banega spectrogram ka)
plt.figure(figsize=(10, 5))
librosa.display.specshow(spectrogram_db, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.savefig('spectrogram_output.png')  # image save ho jayegi
print("Spectrogram image saved as 'spectrogram_output.png'")