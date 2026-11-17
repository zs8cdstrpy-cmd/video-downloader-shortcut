# Video Downloader Shortcut

Simple self-hosted video downloader for **TikTok**, **Instagram**, **Facebook**, and **X (Twitter)**.

Paste a link → Download. Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

> **Disclaimer**:  
> This tool is for personal use only. Downloading content may violate the Terms of Service of the platforms. Only download content you own or have permission to download. The author is not responsible for any misuse.

## Features

- Paste any supported URL
- Best quality video download
- Simple clean web interface
- Works with short links
- Self-hosted (your data stays with you)

## Requirements

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) (recommended for best quality)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/zs8cdstrpy-cmd/video-downloader-shortcut.git
cd video-downloader-shortcut

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Then open: **http://localhost:8000**

## iOS Shortcut (Optional)

You can create a simple iOS Shortcut that:

1. Takes the shared URL
2. Opens your self-hosted server with the URL pre-filled

or use existing free shortcuts like:
- [FREE Media Downloader](https://github.com/nuroctane/free-everything-downloader)
- TVDL

## Supported Platforms

| Platform     | Status          |
|--------------|-----------------|
| TikTok       | ✅ Working      |
| Instagram    | ✅ Working      |
| Facebook     | ✅ Working      |
| X / Twitter  | ✅ Working      |
| YouTube      | ✅ Working      |
| Others       | Via yt-dlp      |

## Notes

- For some Instagram / private content you may need cookies.
- Keep yt-dlp updated: `yt-dlp -U`

## License

MIT
