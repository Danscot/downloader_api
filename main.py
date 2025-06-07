from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download_video(req: DownloadRequest):
    url = req.url
    if not url:
        return JSONResponse(status_code=400, content={"error": "URL is required"})

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
            info = ydl.extract_info(url, download=True)
            filename = f"{video_id}.mp3"

            if not os.path.exists(filename):
                return JSONResponse(status_code=500, content={"error": "Download failed"})

            return FileResponse(
                path=filename,
                filename=info.get("title", "audio") + ".mp3",
                media_type="audio/mpeg",
                background=None,
            )

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

