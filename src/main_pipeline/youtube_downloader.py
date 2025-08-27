# imports 
import yt_dlp
import os 
"""
def youtube_downloader(youtube_url, folder_downloaded_video):
    ydl_opts = {
        'outtmpl': os.path.join(folder_downloaded_video, '%(title)s.%(ext)s'),  # Output filename
        'format': 'bestvideo+bestaudio/best',  # Best quality
        'merge_output_format': 'mp4',  # Ensure MP4 output
    }
    yt_dlp.YoutubeDL()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    return str(ydl_opts['outtmpl'])"""

def youtube_downloader(url: str, folder: str) -> str:
    """
    Downloads the video and returns the full path to the downloaded file.
    """
    final_path = {"name": None}  # mutable container to capture inside nested hook

    def _hook(d: dict):
        # Only capture once when download is fully finished
        if d.get("status") == "finished":
            # yt‑d lp puts the final merged filename here
            full = d.get("info_dict", {}).get("_filename")
            if full:
                final_path["name"] = full

    # Set your outtmpl as you like, e.g.
    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "progress_hooks": [_hook],
        # … optionally verbose/logging settings
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(final_path["name"])