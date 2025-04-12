from pydub import AudioSegment
from pydub.generators import Sine
import os

def create_test_song(filename, duration_ms=3000, sample_rate=44100):
    # Generate a simple sine wave
    sine_wave = Sine(440)  # 440 Hz, standard A note
    audio = sine_wave.to_audio_segment(duration=duration_ms)
    
    # Export as MP3
    audio.export(
        filename,
        format="mp3",
        tags={
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album'
        }
    )
    print(f"Created test MP3: {filename}")

if __name__ == "__main__":
    # Create songs directory if it doesn't exist
    songs_dir = os.path.join(os.path.dirname(__file__), "songs")
    os.makedirs(songs_dir, exist_ok=True)
    
    # Create a few test songs
    songs = [
        "test_song_1.mp3",
        "test_song_2.mp3",
        "test_song_3.mp3"
    ]
    
    for song in songs:
        filepath = os.path.join(songs_dir, song)
        create_test_song(filepath)
