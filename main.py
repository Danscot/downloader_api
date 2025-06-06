from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()  # ✅ Define the app properly for FastAPI

@app.post("/api/download")
async def download_video(request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
            return JSONResponse(content={"error": "URL not provided"}, status_code=400)

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': False,
            'simulate': True,
            'forcejson': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "url": info.get("webpage_url"),
            }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
