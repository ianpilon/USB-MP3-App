from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import mutagen

app = FastAPI(title="DJ USB Server")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where songs are stored (relative to server root)
SONGS_DIR = Path(__file__).parent / "songs"
SONGS_DIR.mkdir(exist_ok=True)

@app.get("/")
async def read_root():
    """Root endpoint to check if server is running."""
    return {"status": "ok", "message": "DJ USB Server is running"}

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
                    "url": f"http://0.0.0.0:8000/songs/{file_path.name}",
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
                    "url": f"http://0.0.0.0:8000/songs/{file_path.name}",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
