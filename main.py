from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid
import httpx

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

def resolve_tiktok_url(url: str) -> str:
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url)
            final_url = str(response.url)
            return final_url
    except Exception:
        return url  # fallback if resolution fails

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    url = req.url.strip()
    if not url:
        return JSONResponse(status_code=400, content={"error": "URL is required"})

    # Try to resolve redirects (especially TikTok explorer URLs)
    resolved_url = resolve_tiktok_url(url)

    # Create a unique filename
    video_id = str(uuid.uuid4())
    output_template = f"{video_id}.%(ext)s"

    # yt-dlp config
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(resolved_url, download=True)
            filename = f"{video_id}.mp3"

            if not os.path.exists(filename):
                return JSONResponse(status_code=500, content={"error": "Download failed"})

            return FileResponse(
                path=filename,
                filename=info.get("title", "audio") + ".mp3",
                media_type="audio/mpeg",
            )

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
