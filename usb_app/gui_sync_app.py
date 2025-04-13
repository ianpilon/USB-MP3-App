import sys
import os
import json
import shutil
import threading
import time
import requests
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Configuration
SERVER_URL = "https://dj-usb-server-usb-mp3-app.onrender.com"
USB_CONFIG_FILE = ".dj_usb_config.json"
MUSIC_DIR = "Music"
CACHE_DIR = ".cache"

class USBSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DJ USB Sync Tool")
        self.root.geometry("500x500")
        self.root.minsize(500, 500)
        
        # Set icon if available
        try:
            if getattr(sys, 'frozen', False):
                # Running as exe
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                # Running as script
                icon_path = "icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        self.usb_path = None
        self.songs = []
        self.sync_thread = None
        self.stop_sync = False
        
        self.create_widgets()
        
        # Check for USB drives automatically
        self.refresh_drives()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        
        # Title
        title = ttk.Label(main_frame, text="DJ USB Sync Tool", style='Header.TLabel')
        title.pack(pady=(0, 20))
        
        # USB Drive selection
        drive_frame = ttk.Frame(main_frame)
        drive_frame.pack(fill=tk.X, pady=10)
        
        drive_label = ttk.Label(drive_frame, text="Select USB Drive:")
        drive_label.pack(anchor=tk.W)
        
        drive_select_frame = ttk.Frame(drive_frame)
        drive_select_frame.pack(fill=tk.X, pady=5)
        
        self.drive_combo = ttk.Combobox(drive_select_frame, state="readonly", font=('Helvetica', 12))
        self.drive_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        refresh_button = ttk.Button(drive_select_frame, text="🔄", width=3, command=self.refresh_drives)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.status_text = tk.Text(status_frame, height=10, wrap=tk.WORD, font=('Helvetica', 11))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.sync_button = ttk.Button(button_frame, text="Sync Music to USB", command=self.start_sync)
        self.sync_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_sync_process, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        exit_button.pack(side=tk.RIGHT, padx=5)
        
        # Version label
        version_label = ttk.Label(main_frame, text="v1.0.0", font=('Helvetica', 8))
        version_label.pack(side=tk.BOTTOM, anchor=tk.SE)
        
    def refresh_drives(self):
        """Detect available drives"""
        self.log_status("Scanning for USB drives...")
        drives = []
        
        # This works on Windows
        if sys.platform == 'win32':
            import win32api
            drive_letters = win32api.GetLogicalDriveStrings().split('\0')[:-1]
            for drive in drive_letters:
                if win32api.GetDriveType(drive) == win32api.DRIVE_REMOVABLE:
                    drives.append(drive)
        
        # This works on macOS and Linux
        else:
            # On macOS, check /Volumes
            if sys.platform == 'darwin':
                volumes_dir = Path('/Volumes')
                if volumes_dir.exists():
                    for item in volumes_dir.iterdir():
                        if item.is_dir() and item.name != 'Macintosh HD':
                            drives.append(str(item))
            
            # On Linux, check /media/username
            elif sys.platform.startswith('linux'):
                username = os.getlogin()
                media_dir = Path(f'/media/{username}')
                if media_dir.exists():
                    for item in media_dir.iterdir():
                        if item.is_dir():
                            drives.append(str(item))
            
            # Also check /mnt directory on Linux
            if sys.platform.startswith('linux'):
                mnt_dir = Path('/mnt')
                if mnt_dir.exists():
                    for item in mnt_dir.iterdir():
                        if item.is_dir():
                            drives.append(str(item))
        
        # Update the combobox
        if drives:
            self.drive_combo['values'] = drives
            self.drive_combo.current(0)
            self.log_status(f"Found {len(drives)} USB drive(s).")
        else:
            self.drive_combo['values'] = ['No USB drives found']
            self.drive_combo.current(0)
            self.log_status("No USB drives found. Please connect a USB drive and refresh.")
    
    def log_status(self, message):
        """Add message to status text widget"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_sync(self):
        """Start the sync process in a separate thread"""
        if self.drive_combo.get() == 'No USB drives found':
            messagebox.showerror("Error", "No USB drive selected. Please connect a USB drive and refresh.")
            return
        
        self.usb_path = Path(self.drive_combo.get())
        if not self.usb_path.exists():
            messagebox.showerror("Error", f"Selected drive {self.usb_path} does not exist.")
            return
        
        # Clear status and reset progress
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # Disable sync button and enable stop button
        self.sync_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_sync = False
        
        # Start sync thread
        self.sync_thread = threading.Thread(target=self.sync_usb)
        self.sync_thread.daemon = True
        self.sync_thread.start()
    
    def stop_sync_process(self):
        """Stop the sync process"""
        self.stop_sync = True
        self.log_status("Stopping sync... please wait.")
        self.stop_button.config(state=tk.DISABLED)
    
    def sync_usb(self):
        """Sync the USB drive with the server"""
        try:
            # Initialize USB if needed
            if not self.is_initialized(self.usb_path):
                self.log_status("USB drive is not initialized. Initializing...")
                self.initialize_usb(self.usb_path)
            
            # Get songs from server
            self.log_status("Connecting to server...")
            songs = self.get_songs_from_server()
            
            if not songs:
                self.log_status("No songs found on the server. Make sure you've uploaded some songs first.")
                self.sync_complete(False)
                return
            
            self.songs = songs
            self.log_status(f"Found {len(songs)} songs on the server.")
            
            # Get existing songs on USB
            music_dir = self.usb_path / MUSIC_DIR
            if not music_dir.exists():
                music_dir.mkdir(parents=True, exist_ok=True)
            
            existing_songs = set(file.name for file in music_dir.glob("*.mp3") if file.is_file())
            
            # Find songs to download and remove
            new_songs = [song for song in songs if song["filename"] not in existing_songs]
            removed_songs = [song for song in existing_songs if song not in set(s["filename"] for s in songs)]
            
            self.log_status(f"\nSync summary:")
            self.log_status(f"- New songs to download: {len(new_songs)}")
            self.log_status(f"- Songs to remove: {len(removed_songs)}")
            
            # Download new songs
            total_songs = len(new_songs) + len(removed_songs)
            processed = 0
            
            # Create cache directory
            cache_dir = self.usb_path / CACHE_DIR
            cache_dir.mkdir(exist_ok=True)
            
            # Download new songs
            for i, song in enumerate(new_songs):
                if self.stop_sync:
                    self.log_status("Sync stopped by user.")
                    self.sync_complete(False)
                    return
                
                self.log_status(f"Downloading: {song['filename']} ({i+1}/{len(new_songs)})")
                
                try:
                    # Download to cache first
                    cache_path = cache_dir / song["filename"]
                    
                    # Download the song
                    response = requests.get(song["url"], stream=True)
                    response.raise_for_status()
                    
                    with open(cache_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if self.stop_sync:
                                break
                            f.write(chunk)
                    
                    if self.stop_sync:
                        continue
                    
                    # Copy to music directory
                    shutil.copy2(cache_path, music_dir / song["filename"])
                    
                    self.log_status(f"✅ Downloaded: {song['filename']}")
                except Exception as e:
                    self.log_status(f"❌ Error downloading {song['filename']}: {e}")
                
                # Update progress
                processed += 1
                self.progress_var.set((processed / total_songs) * 100)
                self.root.update_idletasks()
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(0.2)
            
            # Remove songs that are no longer on the server
            for filename in removed_songs:
                if self.stop_sync:
                    break
                
                try:
                    (music_dir / filename).unlink()
                    self.log_status(f"Removed: {filename}")
                except Exception as e:
                    self.log_status(f"Error removing {filename}: {e}")
                
                # Update progress
                processed += 1
                self.progress_var.set((processed / total_songs) * 100)
                self.root.update_idletasks()
            
            # Update config with last sync time
            self.update_sync_time(self.usb_path)
            
            # List all songs
            all_songs = list(music_dir.glob("*.mp3"))
            self.log_status(f"\nSync complete. Total songs on USB: {len(all_songs)}")
            
            # Show songs (max 10)
            if all_songs:
                self.log_status("\nSongs on USB:")
                for song in sorted(all_songs)[:10]:
                    self.log_status(f"  {song.name}")
                if len(all_songs) > 10:
                    self.log_status(f"  ... and {len(all_songs) - 10} more")
            
            self.sync_complete(True)
            
        except Exception as e:
            self.log_status(f"Error during sync: {str(e)}")
            self.sync_complete(False)
    
    def sync_complete(self, success):
        """Handle sync completion"""
        # Re-enable sync button and disable stop button
        self.sync_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if success and not self.stop_sync:
            self.log_status("\n✅ Sync completed successfully!")
            messagebox.showinfo("Sync Complete", "Your music has been synced to the USB drive successfully!")
        elif self.stop_sync:
            self.log_status("\n⚠️ Sync was stopped by user.")
        else:
            self.log_status("\n❌ Sync failed.")
    
    def is_initialized(self, usb_path):
        """Check if the USB drive is initialized"""
        config_file = usb_path / USB_CONFIG_FILE
        return config_file.exists()
    
    def initialize_usb(self, usb_path):
        """Initialize the USB drive with the necessary directories"""
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
    
    def update_sync_time(self, usb_path):
        """Update the last sync time in the config file"""
        config_file = usb_path / USB_CONFIG_FILE
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                
                config["last_sync"] = time.time()
                
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
            except Exception as e:
                self.log_status(f"Error updating config file: {e}")
    
    def get_songs_from_server(self):
        """Get the list of songs from the server"""
        try:
            response = requests.get(f"{SERVER_URL}/songs")
            response.raise_for_status()
            return response.json().get("songs", [])
        except Exception as e:
            self.log_status(f"Error fetching songs: {e}")
            return []

def main():
    root = tk.Tk()
    app = USBSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
