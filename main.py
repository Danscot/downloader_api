from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import os
from fastapi.responses import FileResponse

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Video Downloader API!"}

# Favicon endpoint (serve a default favicon.ico)
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")  # Add a favicon.ico file to your project folder

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Video download endpoint
@app.post("/api/download")
async def download_video(data: VideoRequest):
    url = data.url
    output_dir = "downloads"

    # Create the folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title).50s.%(ext)s'),
        'format': 'best',
        'noplaylist': True,
        # 'cookiefile': 'cookies.txt',  # Uncomment if you need cookies
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            platform = 'unknown'

            # Auto-detect platform
            if 'tiktok.com' in url:
                platform = 'tiktok'
            elif 'facebook.com' in url:
                platform = 'facebook'
            elif 'instagram.com' in url:
                platform = 'instagram'

            return {
                "status": "success",
                "platform": platform,
                "title": info.get("title"),
                "ext": info.get("ext"),
                "thumbnail": info.get("thumbnail"),
                "filepath": filename
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
