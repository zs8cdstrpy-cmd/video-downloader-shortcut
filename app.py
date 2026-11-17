from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yt_dlp
import os
import uuid
import asyncio
from pathlib import Path

app = FastAPI(title="Video Downloader Shortcut")

# Create downloads folder
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Simple in-memory storage for download status (for demo)
downloads = {}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
        }
        .container {
            max-width: 560px;
            width: 100%;
        }
        h1 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 32px;
            font-size: 0.95rem;
        }
        .card {
            background: #1a1a1a;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #2a2a2a;
        }
        input[type="url"] {
            width: 100%;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid #333;
            background: #111;
            color: #fff;
            font-size: 1rem;
            margin-bottom: 16px;
        }
        input[type="url"]:focus {
            outline: none;
            border-color: #3b82f6;
        }
        button {
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: none;
            background: #3b82f6;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover { background: #2563eb; }
        button:disabled {
            background: #333;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            padding: 14px;
            border-radius: 12px;
            background: #111;
            font-size: 0.9rem;
            display: none;
        }
        .status.show { display: block; }
        .status.error { border: 1px solid #ef4444; color: #fca5a5; }
        .status.success { border: 1px solid #22c55e; color: #86efac; }
        .platforms {
            margin-top: 32px;
            text-align: center;
            color: #666;
            font-size: 0.85rem;
        }
        .platforms span {
            display: inline-block;
            margin: 4px 6px;
            padding: 4px 10px;
            background: #1a1a1a;
            border-radius: 20px;
            border: 1px solid #2a2a2a;
        }
        a.download-link {
            color: #60a5fa;
            text-decoration: none;
            font-weight: 600;
        }
        a.download-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Video Downloader</h1>
        <p class="subtitle">TikTok • Instagram • Facebook • X</p>

        <div class="card">
            <form id="downloadForm">
                <input type="url" id="url" name="url" placeholder="Paste link video di sini..." required>
                <button type="submit" id="btn">Download</button>
            </form>
            <div id="status" class="status"></div>
        </div>

        <div class="platforms">
            <span>TikTok</span>
            <span>Instagram</span>
            <span>Facebook</span>
            <span>X / Twitter</span>
            <span>YouTube</span>
        </div>
    </div>

    <script>
        const form = document.getElementById('downloadForm');
        const statusEl = document.getElementById('status');
        const btn = document.getElementById('btn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('url').value.trim();
            if (!url) return;

            btn.disabled = true;
            btn.textContent = 'Sedang mengunduh...';
            statusEl.className = 'status show';
            statusEl.textContent = 'Memproses link... mohon tunggu.';

            try {
                const res = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ url })
                });

                const data = await res.json();

                if (!res.ok) {
                    throw new Error(data.detail || 'Gagal mengunduh');
                }

                statusEl.className = 'status show success';
                statusEl.innerHTML = `
                    Berhasil!<br>
                    <a class="download-link" href="${data.download_url}" download>
                        💾 Klik di sini untuk menyimpan video
                    </a>
                `;
            } catch (err) {
                statusEl.className = 'status show error';
                statusEl.textContent = 'Error: ' + err.message;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Download';
            }
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.post("/download")
async def download_video(url: str = Form(...)):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL tidak valid")

    video_id = str(uuid.uuid4())[:8]
    output_template = str(DOWNLOAD_DIR / f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Find the actual file
        filepath = Path(filename)
        if not filepath.exists():
            # try common extensions
            for ext in [".mp4", ".webm", ".mkv"]:
                candidate = DOWNLOAD_DIR / f"{video_id}{ext}"
                if candidate.exists():
                    filepath = candidate
                    break

        if not filepath.exists():
            raise Exception("File tidak ditemukan setelah download")

        return {
            "success": True,
            "title": info.get("title", "video"),
            "download_url": f"/file/{filepath.name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/file/{filename}")
async def get_file(filename: str):
    filepath = DOWNLOAD_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="video/mp4"
    )

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Video Downloader berjalan di http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
