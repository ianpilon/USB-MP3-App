import os
import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional
import requests
from datetime import datetime

class USBManager:
    """Manages a DJ USB drive with cloud sync capabilities."""
    
    def __init__(self, usb_path: str, server_url: str):
        self.usb_path = Path(usb_path)
        self.server_url = server_url
        self.music_dir = self.usb_path / "Music"
        self.app_dir = self.usb_path / ".dj-app"
        self.cache_dir = self.app_dir / "cache"
        self.config_file = self.app_dir / "config.json"
        
        # Ensure directories exist
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.app_dir / "sync.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("USBManager")
        
        # Load or create config
        self._load_config()

    def _load_config(self):
        """Load or create configuration file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'last_sync': None,
                'songs': {},  # filename -> {id, size, last_played, cached}
                'server_url': self.server_url
            }
            self._save_config()

    def _save_config(self):
        """Save current configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def initialize_drive(self) -> bool:
        """Initialize a new USB drive for DJ use."""
        try:
            # Create directory structure
            self.logger.info(f"Initializing USB drive at {self.usb_path}")
            
            # Create a README
            readme_path = self.usb_path / "README.txt"
            with open(readme_path, 'w') as f:
                f.write("DJ USB Drive\n\nThis drive is managed by DJ-USB-App. Do not modify files directly.")
            
            # Test server connection
            self.sync()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize drive: {e}")
            return False

    def sync(self) -> bool:
        """Synchronize with server, download new songs, remove deleted ones."""
        try:
            # Get server song list
            response = requests.get(f"{self.server_url}/songs")
            server_songs = response.json()['songs']
            
            # Track changes
            new_songs = []
            removed_songs = []
            
            # Check for new or updated songs
            for song in server_songs:
                if song['filename'] not in self.config['songs']:
                    new_songs.append(song)
                    
            # Check for removed songs
            local_songs = set(self.config['songs'].keys())
            server_song_names = {s['filename'] for s in server_songs}
            removed_songs = local_songs - server_song_names
            
            # Download new songs
            for song in new_songs:
                self._download_song(song)
                
            # Remove deleted songs
            for filename in removed_songs:
                self._remove_song(filename)
            
            # Update last sync time
            self.config['last_sync'] = datetime.now().isoformat()
            self._save_config()
            
            self.logger.info(f"Sync complete. Added: {len(new_songs)}, Removed: {len(removed_songs)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            return False

    def _download_song(self, song: Dict):
        """Download a song from the server."""
        try:
            response = requests.get(
                f"{self.server_url}/songs/{song['filename']}",
                stream=True
            )
            response.raise_for_status()
            
            file_path = self.music_dir / song['filename']
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.config['songs'][song['filename']] = {
                'id': song.get('id'),
                'size': song.get('size'),
                'last_played': None,
                'cached': True
            }
            self._save_config()
            
            self.logger.info(f"Downloaded: {song['filename']}")
            
        except Exception as e:
            self.logger.error(f"Failed to download {song['filename']}: {e}")

    def _remove_song(self, filename: str):
        """Remove a song from the USB drive."""
        try:
            file_path = self.music_dir / filename
            if file_path.exists():
                file_path.unlink()
            
            if filename in self.config['songs']:
                del self.config['songs'][filename]
                self._save_config()
                
            self.logger.info(f"Removed: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to remove {filename}: {e}")

    def get_song_list(self) -> List[Dict]:
        """Get list of all songs on the drive."""
        return [
            {
                'filename': filename,
                **details
            }
            for filename, details in self.config['songs'].items()
        ]

    def update_last_played(self, filename: str):
        """Update the last played time for a song."""
        if filename in self.config['songs']:
            self.config['songs'][filename]['last_played'] = datetime.now().isoformat()
            self._save_config()
