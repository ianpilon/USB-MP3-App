#!/usr/bin/env python3
# DJ USB Tool - Simple version for direct download
# This is a simplified version that users can run directly without compilation

import os
import sys
import json
import shutil
import requests
from pathlib import Path
import time

# Configuration
SERVER_URL = "https://dj-usb-server-usb-mp3-app.onrender.com"
USB_CONFIG_FILE = ".dj_usb_config.json"
MUSIC_DIR = "Music"
CACHE_DIR = ".cache"

# Utility functions
def get_usb_root():
    """Get the USB drive root directory (current directory)."""
    return Path(os.getcwd())

def initialize_usb(usb_path):
    """Initialize the USB drive with the necessary directories."""
    # Create directories
    music_dir = usb_path / MUSIC_DIR
    cache_dir = usb_path / CACHE_DIR
    
    music_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)
    
    # Create or update config file
    config_file = usb_path / USB_CONFIG_FILE
    config = {
        "initialized": True,
        "server_url": SERVER_URL,
        "last_sync": None,
        "version": "1.0.0"
    }
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    return True

def is_initialized(usb_path):
    """Check if the USB drive is initialized."""
    config_file = usb_path / USB_CONFIG_FILE
    return config_file.exists()

def get_songs_from_server():
    """Get the list of songs from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/songs")
        response.raise_for_status()
        return response.json().get("songs", [])
    except Exception as e:
        print(f"Error fetching songs: {e}")
        return []

def download_song(song, usb_path):
    """Download a song to the USB drive."""
    try:
        # Create cache directory if it doesn't exist
        cache_dir = usb_path / CACHE_DIR
        cache_dir.mkdir(exist_ok=True)
        
        # Download to cache first
        cache_path = cache_dir / song["filename"]
        
        # Download the song
        response = requests.get(song["url"], stream=True)
        response.raise_for_status()
        
        with open(cache_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Copy to music directory
        music_dir = usb_path / MUSIC_DIR
        music_dir.mkdir(exist_ok=True)
        
        shutil.copy2(cache_path, music_dir / song["filename"])
        
        print(f"Downloaded: {song['filename']}")
        return True
    except Exception as e:
        print(f"Error downloading {song['filename']}: {e}")
        return False

def sync_usb(usb_path):
    """Sync the USB drive with the server."""
    if not is_initialized(usb_path):
        print("USB drive is not initialized. Initializing...")
        initialize_usb(usb_path)
    
    # Get songs from server
    songs = get_songs_from_server()
    
    if not songs:
        print("No songs found on the server. Make sure you've uploaded some songs first.")
        return
    
    print(f"Found {len(songs)} songs on the server.")
    
    # Get existing songs on USB
    music_dir = usb_path / MUSIC_DIR
    existing_songs = set(file.name for file in music_dir.glob("*.mp3") if file.is_file())
    
    # Download new songs
    new_songs = [song for song in songs if song["filename"] not in existing_songs]
    removed_songs = [song for song in existing_songs if song not in set(s["filename"] for s in songs)]
    
    print(f"\nSyncing songs:")
    print(f"- New songs to download: {len(new_songs)}")
    print(f"- Songs to remove: {len(removed_songs)}")
    
    # Download new songs
    downloaded = 0
    for song in new_songs:
        success = download_song(song, usb_path)
        if success:
            downloaded += 1
            # Add a small delay to avoid overwhelming the server
            time.sleep(0.2)
    
    # Remove songs that are no longer on the server
    removed = 0
    for filename in removed_songs:
        try:
            (music_dir / filename).unlink()
            removed += 1
        except Exception as e:
            print(f"Error removing {filename}: {e}")
    
    # Update config with last sync time
    config_file = usb_path / USB_CONFIG_FILE
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            config["last_sync"] = time.time()
            
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error updating config file: {e}")
    
    print(f"\nSync complete. Added: {downloaded}, Removed: {removed}")
    
    # List all songs
    all_songs = list(music_dir.glob("*.mp3"))
    print(f"Total songs on USB: {len(all_songs)}")
    
    # Show songs (max 10)
    if all_songs:
        print("\nSongs on USB:")
        for song in sorted(all_songs)[:10]:
            print(f"  {song.name}")
        if len(all_songs) > 10:
            print(f"  ... and {len(all_songs) - 10} more")

def show_help():
    """Show help information."""
    print("DJ USB Tool - Command Line Interface")
    print("====================================")
    print("\nCommands:")
    print("  init    - Initialize the USB drive")
    print("  sync    - Sync music from server to USB drive")
    print("  status  - Show status of USB drive")
    print("  help    - Show this help message")
    print("\nExample:")
    print("  python dj_usb_tool.py sync")

def show_status(usb_path):
    """Show status of the USB drive."""
    if not is_initialized(usb_path):
        print("USB drive is not initialized.")
        return
    
    # Read config
    config_file = usb_path / USB_CONFIG_FILE
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        print("DJ USB Drive Status")
        print("==================")
        print(f"Server URL: {config.get('server_url', 'Not set')}")
        
        last_sync = config.get('last_sync')
        if last_sync:
            last_sync_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_sync))
            print(f"Last sync: {last_sync_str}")
        else:
            print("Last sync: Never")
        
        # Count songs
        music_dir = usb_path / MUSIC_DIR
        songs = list(music_dir.glob("*.mp3"))
        print(f"\nTotal songs: {len(songs)}")
        
        # Show songs (max 10)
        if songs:
            print("\nSongs:")
            for song in sorted(songs)[:10]:
                print(f"  [✓] {song.name}")
            if len(songs) > 10:
                print(f"  ... and {len(songs) - 10} more")
        
    except Exception as e:
        print(f"Error reading config: {e}")

def main():
    """Main function."""
    # Get USB root directory (current directory)
    usb_path = get_usb_root()
    
    # Print header
    print("\nDJ USB Tool v1.0.0")
    print("=================\n")
    
    # Process command line arguments
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "init":
        if is_initialized(usb_path):
            print("USB drive is already initialized.")
            choice = input("Do you want to re-initialize? (y/n): ")
            if choice.lower() != "y":
                return
        
        success = initialize_usb(usb_path)
        if success:
            print("USB drive initialized successfully.")
        else:
            print("Failed to initialize USB drive.")
    
    elif command == "sync":
        sync_usb(usb_path)
    
    elif command == "status":
        show_status(usb_path)
    
    else:
        print(f"Unknown command: {command}")
        show_help()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
