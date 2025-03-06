from flask import Flask, request, render_template, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]
        if file.filename == "":
            return "No selected file"

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Process the video (merge video & audio)
        output_filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)
        
        try:
            clip = VideoFileClip(file_path)
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            clip.close()
        except Exception as e:
            return f"Error processing video: {str(e)}"

        return render_template("upload.html", download_link=f"/download/{output_filename}")

    return render_template("upload.html", download_link=None)

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["PROCESSED_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
