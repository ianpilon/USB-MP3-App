import os
import sys
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import requests
import mutagen
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SongMetadata:
    """Represents metadata for a song."""
    title: str
    filename: str
    url: str
    size: int
    duration: Optional[int] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    local_path: Optional[str] = None

class VirtualDrive:
    """Manages a virtual USB drive that caches songs from the server."""
    
    def __init__(self, server_url: str, cache_dir: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(tempfile.gettempdir()) / "dj_usb_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize song cache
        self.songs: Dict[str, SongMetadata] = {}
        self.refresh_song_list()
        
    def refresh_song_list(self) -> None:
        """Fetch the current list of songs from the server."""
        try:
            logger.info(f"Fetching songs from {self.server_url}/songs")
            response = requests.get(
                f"{self.server_url}/songs",
                timeout=10  # Add timeout
            )
            response.raise_for_status()
            
            songs_data = response.json()["songs"]
            logger.info(f"Found {len(songs_data)} songs on server")
            
            for song_data in songs_data:
                filename = song_data["filename"]
                self.songs[filename] = SongMetadata(
                    title=song_data.get("title", filename),
                    filename=filename,
                    url=song_data["url"],
                    size=song_data["size"],
                    duration=song_data.get("duration"),
                    artist=song_data.get("artist"),
                    album=song_data.get("album"),
                    local_path=self._get_cached_path(filename)
                )
                logger.info(f"Added song: {filename} (cached: {bool(self._get_cached_path(filename))})")
        except requests.Timeout:
            logger.error("Server connection timed out. Is the server running?")
        except requests.ConnectionError:
            logger.error("Could not connect to server. Check your internet connection.")
        except Exception as e:
            logger.error(f"Failed to refresh song list: {e}")
            
    def _get_cached_path(self, filename: str) -> Optional[str]:
        """Get the local path for a cached song."""
        cached_file = self.cache_dir / filename
        return str(cached_file) if cached_file.exists() else None
    
    def download_song(self, filename: str) -> Optional[str]:
        """Download a song from the server and cache it locally."""
        if filename not in self.songs:
            logger.error(f"Song not found: {filename}")
            return None
            
        song = self.songs[filename]
        cached_path = Path(self.cache_dir / filename)
        
        if cached_path.exists():
            logger.info(f"Song already cached: {filename}")
            return str(cached_path)
            
        try:
            response = requests.get(song.url, stream=True)
            response.raise_for_status()
            
            with open(cached_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            song.local_path = str(cached_path)
            logger.info(f"Downloaded and cached: {filename}")
            return str(cached_path)
            
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            if cached_path.exists():
                cached_path.unlink()
            return None
    
    def get_song_path(self, filename: str) -> Optional[str]:
        """Get the path to a song, downloading it if necessary."""
        if filename not in self.songs:
            return None
            
        song = self.songs[filename]
        if not song.local_path:
            song.local_path = self.download_song(filename)
        
        return song.local_path
    
    def list_songs(self) -> List[SongMetadata]:
        """Get a list of all available songs."""
        return list(self.songs.values())
    
    def clear_cache(self) -> None:
        """Clear the local song cache."""
        try:
            for file in self.cache_dir.glob("*.mp3"):
                file.unlink()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

if __name__ == "__main__":
    # Test the virtual drive
    drive = VirtualDrive("https://dj-usb-server-usb-mp3-app.onrender.com")
    print("\nAvailable songs:")
    for song in drive.list_songs():
        print(f"- {song.title} ({song.filename})")
        if not song.local_path:
            path = drive.get_song_path(song.filename)
            if path:
                print(f"  Downloaded to: {path}")
