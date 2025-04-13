# DJ USB Virtual Drive

This application creates a virtual USB drive that connects to the DJ USB Server, allowing you to access your MP3 collection as if it were on a physical USB drive. Perfect for use with DJ software like Serato.

## Features

- Appears as a real USB drive to your system
- Automatically downloads and caches songs as needed
- Maintains song metadata (title, artist, album)
- Works offline with previously cached songs
- Easy to use command-line interface

## Requirements

- Python 3.7 or higher
- FUSE for macOS/Linux
- Internet connection for initial song downloads

### macOS Requirements

Install macOS FUSE:
```bash
brew install macfuse
```

## Installation

1. Make sure you have all requirements installed
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Mount the Virtual Drive

```bash
# Mount with default settings
python cli.py mount

# Mount with custom settings
python cli.py mount --mount-point ~/Desktop/MyDJDrive --cache-dir ~/.my-dj-cache
```

### Unmount the Drive

```bash
# Unmount with default mount point
python cli.py unmount

# Unmount from custom location
python cli.py unmount --mount-point ~/Desktop/MyDJDrive
```

### Clear the Cache

```bash
# Clear the default cache
python cli.py clear-cache

# Clear a custom cache directory
python cli.py clear-cache --cache-dir ~/.my-dj-cache
```

## Default Locations

- Mount Point: `~/Desktop/DJ-USB-Drive`
- Cache Directory: `~/.dj-usb-cache`
- Server URL: `https://dj-usb-server-usb-mp3-app.onrender.com`

## Troubleshooting

1. If mounting fails:
   - Ensure macFUSE is installed
   - Check if the mount point is already in use
   - Try unmounting first if the drive is already mounted

2. If songs don't appear:
   - Check your internet connection
   - Verify the server is running
   - Try clearing the cache

3. Permission errors:
   - Ensure you have write access to the mount point
   - Ensure you have write access to the cache directory
