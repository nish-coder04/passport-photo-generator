import os
import io
import cv2
import numpy as np
from rembg import remove
from PIL import Image

# Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "static", "inputs")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "static", "outputs")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Passport photo size (35mm x 45mm at 300 DPI)
PASSPORT_WIDTH = int(35 * 300 / 25.4)   # ~413 px
PASSPORT_HEIGHT = int(45 * 300 / 25.4)  # ~531 px

BACKGROUND_COLORS = {
    "white": (255, 255, 255, 255),
    "blue":  (67, 114, 196, 255),
    "transparent": (0, 0, 0, 0),
}

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_and_crop_face(pil_image):
    cv_img = cv2.cvtColor(np.array(pil_image.convert("RGB")), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    img_w, img_h = pil_image.size

    if len(faces) > 0:
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        fx, fy, fw, fh = faces[0]

        pad_top    = int(fh * 0.6)
        pad_bottom = int(fh * 1.8)
        pad_side   = int(fw * 0.7)

        x1 = max(0, fx - pad_side)
        y1 = max(0, fy - pad_top)
        x2 = min(img_w, fx + fw + pad_side)
        y2 = min(img_h, fy + fh + pad_bottom)

        cropped = pil_image.crop((x1, y1, x2, y2))
    else:
        crop_h = int(img_h * 0.6)
        margin = int(img_w * 0.1)
        cropped = pil_image.crop((margin, 0, img_w - margin, crop_h))

    return cropped


def remove_background(input_path, output_path, bg_color="white"):
    with open(input_path, "rb") as f:
        input_data = f.read()

    output_data = remove(input_data)
    image = Image.open(io.BytesIO(output_data)).convert("RGBA")

    cropped = detect_and_crop_face(image)
    cropped.thumbnail((PASSPORT_WIDTH, PASSPORT_HEIGHT), Image.LANCZOS)

    bg_rgba = BACKGROUND_COLORS.get(bg_color, (255, 255, 255, 255))
    background = Image.new("RGBA", (PASSPORT_WIDTH, PASSPORT_HEIGHT), bg_rgba)

    offset_x = (PASSPORT_WIDTH - cropped.width) // 2
    offset_y = (PASSPORT_HEIGHT - cropped.height) // 2
    background.paste(cropped, (offset_x, offset_y), cropped)

    if bg_color == "transparent":
        background.save(output_path, "PNG")
    else:
        background.convert("RGB").save(output_path, "PNG")
