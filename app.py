import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
from utils import remove_background, allowed_file, INPUT_FOLDER, OUTPUT_FOLDER

app = Flask(__name__)
app.secret_key = "passport_secret_2024"

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded.")
            return redirect(request.url)

        file = request.files["file"]
        bg_color = request.form.get("bg_color", "white")

        if file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            input_path = os.path.join(INPUT_FOLDER, file.filename)
            output_filename = os.path.splitext(file.filename)[0] + f"_passport_{bg_color}.png"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            file.save(input_path)
            remove_background(input_path, output_path, bg_color)

            return redirect(url_for("result", filename=output_filename))
        else:
            flash("Invalid file. Please upload PNG, JPG or JPEG.")
            return redirect(request.url)

    return render_template("index.html")

@app.route("/result/<filename>")
def result(filename):
    return render_template("result.html", filename=filename)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route("/preview/<filename>")
def preview_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
