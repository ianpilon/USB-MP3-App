from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from auth import verify_token, create_access_token
from pathlib import Path
import os
import sys
import logging
import mutagen
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DJ USB Server",
    description="API for managing DJ music files with secure upload functionality"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment configuration
PRODUCTION = os.environ.get("RENDER", "false").lower() == "true"
BASE_URL = "https://dj-usb-server-usb-mp3-app.onrender.com" if PRODUCTION else "http://0.0.0.0:8000"

logger.info(f"Starting server in {'production' if PRODUCTION else 'development'} mode")
logger.info(f"Base URL: {BASE_URL}")

# Directory where songs are stored
if PRODUCTION:
    SONGS_DIR = Path("/tmp/songs")
else:
    SONGS_DIR = Path(__file__).parent / "songs"

try:
    SONGS_DIR.mkdir(exist_ok=True, parents=True)
    logger.info(f"Songs directory created at: {SONGS_DIR}")
    logger.info(f"Songs directory permissions: {oct(SONGS_DIR.stat().st_mode)[-3:]}")
except Exception as e:
    logger.error(f"Failed to create songs directory: {e}")

@app.get("/")
async def read_root():
    """Root endpoint to check if server is running."""
    return RedirectResponse(url="/web/")

@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "status": "ok",
        "message": "DJ USB Server is running",
        "environment": "production" if PRODUCTION else "development",
        "base_url": BASE_URL
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with system status."""
    try:
        songs_count = len(list(SONGS_DIR.glob("*.mp3")))
        return {
            "status": "healthy",
            "songs_directory": str(SONGS_DIR),
            "songs_count": songs_count,
            "environment": "production" if PRODUCTION else "development",
            "base_url": BASE_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Free tier limits
FREE_TIER_SONG_LIMIT = 25

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    token: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Upload an MP3 file to the server."""
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files are allowed")
    
    try:
        # Check for free tier limits
        song_count = len(list(SONGS_DIR.glob("*.mp3")))
        if song_count >= FREE_TIER_SONG_LIMIT:
            # In a real system, we would check the user's subscription status
            # For now, we'll just enforce the limit for everyone
            return JSONResponse(
                status_code=402,  # Payment Required
                content={
                    "error": "Free tier limit reached",
                    "detail": f"You have reached the free tier limit of {FREE_TIER_SONG_LIMIT} songs. Please upgrade to upload more songs.",
                    "current_count": song_count,
                    "limit": FREE_TIER_SONG_LIMIT,
                    "upgrade_url": f"{request.base_url}web/#pricing"
                }
            )
        
        file_path = SONGS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Verify it's a valid MP3
        try:
            audio = mutagen.File(file_path)
            if not audio:
                file_path.unlink()  # Delete invalid file
                raise HTTPException(status_code=400, detail="Invalid MP3 file")
        except Exception as e:
            file_path.unlink()  # Delete invalid file
            raise HTTPException(status_code=400, detail=f"Invalid MP3 file: {str(e)}")
        
        # Return song count information along with the upload result
        return {
            "filename": file.filename, 
            "size": len(content),
            "song_count": song_count + 1,
            "limit": FREE_TIER_SONG_LIMIT,
            "remaining": FREE_TIER_SONG_LIMIT - (song_count + 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/token")
async def get_upload_token():
    """Get a temporary token for file uploads."""
    # In production, you would verify credentials here
    token = create_access_token({"sub": "upload_user"})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint that returns a simple audio metadata structure."""
    return {
        "test_song": {
            "title": "Test Audio",
            "artist": "Test Artist",
            "album": "Test Album",
            "duration": 180,  # 3 minutes
            "size": 1024 * 1024 * 3,  # 3MB
            "url": f"{BASE_URL}/songs/test.mp3"
        },
        "server_info": {
            "environment": "production" if PRODUCTION else "development",
            "base_url": BASE_URL,
            "songs_directory": str(SONGS_DIR)
        }
    }

@app.get("/songs")
async def list_songs():
    """List all available songs with metadata."""
    try:
        songs = []
        for file_path in SONGS_DIR.glob("*.mp3"):
            try:
                audio = mutagen.File(file_path)
                metadata = {
                    "title": file_path.stem,
                    "filename": file_path.name,
                    "url": f"{BASE_URL}/songs/{file_path.name}",
                    "size": file_path.stat().st_size,
                    "duration": int(audio.info.length) if audio else None,
                }
                
                # Extract ID3 tags if available
                if hasattr(audio, "tags") and audio.tags:
                    tags = audio.tags
                    if "TIT2" in tags:  # Title
                        metadata["title"] = str(tags["TIT2"])
                    if "TPE1" in tags:  # Artist
                        metadata["artist"] = str(tags["TPE1"])
                    if "TALB" in tags:  # Album
                        metadata["album"] = str(tags["TALB"])
                
                songs.append(metadata)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                # Include basic info even if metadata extraction fails
                songs.append({
                    "title": file_path.stem,
                    "filename": file_path.name,
                    "url": f"{BASE_URL}/songs/{file_path.name}",
                    "size": file_path.stat().st_size,
                })
        
        return JSONResponse(content={"songs": songs})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/songs/{filename}")
async def get_song(filename: str):
    """Stream a specific song file."""
    file_path = SONGS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Song not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Accept-Ranges": "bytes"}
    )

# Mount the static files
try:
    static_dir = Path(__file__).parent / "static_web"
    app.mount("/web", StaticFiles(directory=static_dir, html=True), name="web")
    logger.info(f"Static web files mounted at /web from {static_dir}")
except Exception as e:
    logger.error(f"Failed to mount static web files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
