# Webpage to Video Converter  
A web‑app version of the desktop tool that captures webpage frames via Selenium, converts them into a video, supports slow‑motion, different formats & browsers.

## Features  
- Accepts a URL of an HTML/web‑page.  
- Lets user set: output filename, FPS, duration, window size (WxH), video speed, format (MP4/AVI/MKV/WEBP), browser (Chrome/Firefox), slow‑motion option.  
- Uses headless browser automation (Selenium) to capture screenshots.  
- Compiles screenshots into a video using OpenCV (or FFmpeg for slow‑motion).  
- Downloads the resulting video file to the user.

## Tech stack  
- Python + Flask for the web server (`app.py`).  
- Selenium WebDriver for Chrome/Firefox.  
- OpenCV (headless) + Pillow for video creation.  
- Hosted on Render.

## 🛠️ Setup & Local Testing  
1. Clone the repo:  
   ```bash
   git clone https://github.com/Creatives‑life/webpage_to_video.git  
   cd webpage_to_video  
