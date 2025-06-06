import yt_dlp
import requests

def resolve_redirect(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print("Redirect resolution error:", e)
        return url  # fallback

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    final_url = resolve_redirect(url)
    print(f"Resolved URL: {final_url}")

    ydl_opts = {
        'quiet': True,
        'format': 'mp4',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(final_url, download=False)
            file_url = ydl.prepare_filename(info)
            return jsonify({
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'filepath': f"/static/{os.path.basename(file_url)}"
            })
    except Exception as e:
        print("Download error:", str(e))
        return jsonify({'error': 'Download failed', 'details': str(e)}), 500
