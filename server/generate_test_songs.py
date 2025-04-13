import os
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import subprocess

def generate_sine_wave(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave

def create_test_mp3(filename, freq=440, duration=3):
    # Generate a simple sine wave
    sample_rate = 44100
    audio_data = generate_sine_wave(freq, duration, sample_rate)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Save as WAV first
    wav_path = "temp.wav"
    wavfile.write(wav_path, sample_rate, audio_data)
    
    # Convert to MP3 using ffmpeg
    subprocess.run([
        "ffmpeg", "-y",
        "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-qscale:a", "2",
        filename
    ], capture_output=True)
    
    # Clean up WAV file
    os.remove(wav_path)

def main():
    songs_dir = Path(__file__).parent / "songs"
    songs_dir.mkdir(exist_ok=True)
    
    # Generate 3 test songs with different frequencies
    frequencies = [440, 523, 659]  # A4, C5, E5 notes
    
    for i, freq in enumerate(frequencies, 1):
        filename = songs_dir / f"test_song_{i}.mp3"
        print(f"Generating {filename}")
        create_test_mp3(str(filename), freq)
        print(f"Created test song {i} at {freq}Hz")

if __name__ == "__main__":
    main()
