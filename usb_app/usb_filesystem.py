import os
import sys
import errno
import logging
from pathlib import Path
from typing import Dict, List, Optional
from fuse import FUSE, FuseOSError, Operations
from virtual_drive import VirtualDrive, SongMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class USBFileSystem(Operations):
    """FUSE filesystem that presents songs as if they were on a USB drive."""

    def __init__(self, server_url: str, cache_dir: Optional[str] = None):
        self.virtual_drive = VirtualDrive(server_url, cache_dir)
        self.files: Dict[str, SongMetadata] = {}
        self.refresh_files()
        logger.info(f"Initialized filesystem with {len(self.files)} files")
        
        # Create cache directory if it doesn't exist
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    def refresh_files(self) -> None:
        """Update the file listing from the virtual drive."""
        self.files = {
            f"/{song.filename}": song
            for song in self.virtual_drive.list_songs()
        }
        logger.info(f"Refreshed file listing: {len(self.files)} files available")

    # Filesystem methods
    def getattr(self, path: str, fh=None):
        """Get file attributes."""
        if path == '/':
            return {
                'st_mode': 0o40755,  # directory with 755 permissions
                'st_nlink': 2,
                'st_size': 0,
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0,
                'st_uid': os.getuid(),
                'st_gid': os.getgid()
            }

        if path in self.files:
            song = self.files[path]
            return {
                'st_mode': 0o100644,  # file with 644 permissions
                'st_nlink': 1,
                'st_size': song.size,
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0,
                'st_uid': os.getuid(),
                'st_gid': os.getgid()
            }

        raise FuseOSError(errno.ENOENT)

    def readdir(self, path: str, fh) -> List[str]:
        """List directory contents."""
        if path != '/':
            raise FuseOSError(errno.ENOENT)
        
        # Always include . and ..
        dirents = ['.', '..']
        
        # Add all song filenames
        dirents.extend(song.filename for song in self.virtual_drive.list_songs())
        
        return dirents

    def open(self, path: str, flags):
        """Open a file and ensure it's cached locally."""
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        
        # Download the file if it's not cached
        song = self.files[path]
        local_path = self.virtual_drive.get_song_path(song.filename)
        if not local_path:
            raise FuseOSError(errno.EIO)
        
        return 0

    def read(self, path: str, size: int, offset: int, fh) -> bytes:
        """Read data from a file."""
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        
        song = self.files[path]
        local_path = self.virtual_drive.get_song_path(song.filename)
        if not local_path:
            raise FuseOSError(errno.EIO)
        
        with open(local_path, 'rb') as f:
            f.seek(offset)
            return f.read(size)

def mount_usb_drive(mount_point: str, server_url: str, cache_dir: Optional[str] = None):
    """Mount the virtual USB drive at the specified mount point."""
    # Ensure mount point exists
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
    
    # Ensure mount point is empty
    try:
        if os.path.ismount(mount_point):
            logger.info(f"Unmounting existing mount at {mount_point}")
            if sys.platform == 'darwin':
                os.system(f'diskutil unmount "{mount_point}"')
            else:
                os.system(f'fusermount -u "{mount_point}"')
    except Exception as e:
        logger.warning(f"Failed to unmount existing mount: {e}")
    
    logger.info(f"Mounting USB drive at {mount_point}")
    logger.info(f"Server URL: {server_url}")
    logger.info(f"Cache directory: {cache_dir or 'default'}")
    
    # Initialize filesystem
    fs = USBFileSystem(server_url, cache_dir)
    
    # Mount with FUSE
    FUSE(
        fs,
        mount_point,
        nothreads=True,
        foreground=True,
        allow_other=True,
        volname="DJ USB Drive"
    )

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <mount_point>")
        sys.exit(1)
    
    mount_point = sys.argv[1]
    server_url = "https://dj-usb-server-usb-mp3-app.onrender.com"
    
    try:
        mount_usb_drive(mount_point, server_url)
    except KeyboardInterrupt:
        logger.info("Unmounting USB drive...")
