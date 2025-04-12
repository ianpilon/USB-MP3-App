import requests
import sys
from pathlib import Path

def upload_mp3(server_url: str, mp3_path: str):
    """Upload an MP3 file to the server."""
    # Get upload token
    token_response = requests.post(f"{server_url}/auth/token")
    token_data = token_response.json()
    
    if not token_response.ok:
        print(f"Failed to get token: {token_data}")
        return
    
    # Prepare headers with token
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }
    
    # Upload file
    with open(mp3_path, "rb") as f:
        files = {"file": (Path(mp3_path).name, f, "audio/mpeg")}
        response = requests.post(
            f"{server_url}/upload",
            headers=headers,
            files=files
        )
    
    if response.ok:
        print(f"Successfully uploaded {mp3_path}")
        print(response.json())
    else:
        print(f"Upload failed: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_test.py path/to/song.mp3")
        sys.exit(1)
    
    server_url = "https://dj-usb-server-usb-mp3-app.onrender.com"
    mp3_path = sys.argv[1]
    
    if not Path(mp3_path).exists():
        print(f"File not found: {mp3_path}")
        sys.exit(1)
    
    if not mp3_path.endswith(".mp3"):
        print("Only MP3 files are supported")
        sys.exit(1)
    
    upload_mp3(server_url, mp3_path)
