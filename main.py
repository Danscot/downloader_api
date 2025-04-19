from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/api/download")
async def download_video(data: VideoRequest):
    url = data.url
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title).50s.%(ext)s'),
        'format': 'best',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            platform = 'unknown'
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

