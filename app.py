from flask import Flask, render_template, request, send_file
import os
import time
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from PIL import Image
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    html_url = request.form["html_url"]
    output_filename = request.form["output_filename"]
    frame_rate = int(request.form["fps"])
    duration = int(request.form["duration"])
    window_size_str = request.form["window_size"]
    video_speed = float(request.form["video_speed"])
    video_format = request.form["video_format"]
    browser_choice = request.form["browser_choice"]
    enable_slowdown = "enable_slowdown" in request.form

    try:
        width, height = map(int, window_size_str.split(","))
    except:
        return "Invalid window size format. Use Width,Height"

    output_dir = "frames"
    os.makedirs(output_dir, exist_ok=True)

    # Setup browser
    if browser_choice == "Chrome":
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={width},{height}")
        service = ChromeService("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument(f"--width={width}")
        options.add_argument(f"--height={height}")
        service = FirefoxService("/usr/local/bin/geckodriver")
        driver = webdriver.Firefox(service=service, options=options)

    driver.get(html_url)
    time.sleep(2)

    total_frames = frame_rate * duration
    for frame in range(total_frames):
        frame_path = os.path.join(output_dir, f"frame_{frame:04d}.jpg")
        driver.save_screenshot(frame_path)
        time.sleep(1 / frame_rate)

    driver.quit()

    frame_files = sorted(os.listdir(output_dir))
    first_frame = Image.open(os.path.join(output_dir, frame_files[0]))
    width, height = first_frame.size

    fourcc_dict = {
        "MP4": cv2.VideoWriter_fourcc(*'mp4v'),
        "AVI": cv2.VideoWriter_fourcc(*'XVID'),
        "MKV": cv2.VideoWriter_fourcc(*'X264'),
        "WEBP": cv2.VideoWriter_fourcc(*'VP80'),
    }

    output_video = f"{output_filename}.{video_format.lower()}"
    fourcc = fourcc_dict.get(video_format, fourcc_dict["MP4"])
    video = cv2.VideoWriter(output_video, fourcc, frame_rate, (width, height))

    for frame_file in frame_files:
        frame_path = os.path.join(output_dir, frame_file)
        frame = cv2.imread(frame_path)
        repeat_frames = 2 if enable_slowdown else 1
        for _ in range(repeat_frames):
            video.write(frame)

    video.release()

    if enable_slowdown:
        speed_adjusted_video = f"slow_{output_video}"
        subprocess.call(['ffmpeg', '-y', '-i', output_video, '-filter:v', f'setpts={video_speed}*PTS', speed_adjusted_video])
        return send_file(speed_adjusted_video, as_attachment=True)
    else:
        return send_file(output_video, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
