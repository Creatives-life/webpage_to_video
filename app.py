import os
import time
import cv2
from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <h1>Webpage to Video Converter</h1>
    <form action="/generate" method="post">
        HTML URL: <input type="text" name="url" value="https://ipfs.io/ipfs/"><br>
        Output Filename: <input type="text" name="filename" value="output"><br>
        Frame Rate (FPS): <input type="number" name="fps" value="15"><br>
        Duration (Seconds): <input type="number" name="duration" value="10"><br>
        Window Size (WxH): <input type="text" name="window" value="1280,720"><br>
        Video Speed: <input type="number" step="0.1" name="speed" value="2.0"><br>
        <input type="submit" value="Generate Video">
    </form>
    """

@app.route('/generate', methods=['POST'])
def generate_video():
    url = request.form.get('url')
    filename = request.form.get('filename')
    fps = int(request.form.get('fps', 15))
    duration = int(request.form.get('duration', 10))
    window_size = request.form.get('window', '1280,720')
    video_speed = float(request.form.get('speed', 2.0))

    try:
        width, height = map(int, window_size.split(","))
    except:
        return "Window size format error. Use Width,Height"

    os.makedirs("frames", exist_ok=True)

    # Selenium Chrome Headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={width},{height}")
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    time.sleep(2)

    total_frames = fps * duration
    for frame in range(total_frames):
        driver.save_screenshot(f"frames/frame_{frame:04d}.png")
        time.sleep(1 / fps)

    driver.quit()

    # Create video using OpenCV
    frame_files = sorted(os.listdir("frames"))
    if not frame_files:
        return "No frames captured"

    first_frame = Image.open(os.path.join("frames", frame_files[0]))
    width, height = first_frame.size

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_video = f"{filename}.mp4"
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    for frame_file in frame_files:
        frame = cv2.imread(os.path.join("frames", frame_file))
        video.write(frame)
    video.release()

    # Optional: slow motion
    slow_video = f"slow_{output_video}"
    os.system(f'ffmpeg -y -i "{output_video}" -filter:v "setpts={video_speed}*PTS" "{slow_video}"')

    return f"Video generated: <a href='/{slow_video}'>{slow_video}</a>"

@app.route('/<path:filename>')
def serve_file(filename):
    return app.send_static_file(filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
