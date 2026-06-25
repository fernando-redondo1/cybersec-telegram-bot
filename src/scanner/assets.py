import urllib.request

from PIL import ImageFont

from .constants import (FONTS_DIR, MODELS_DIR,
                         ROBOTO_URL, ROBOTO_BOLD_URL,
                         DETECTOR_URL, LANDMARKER_URL)


def download_if_missing(path, url, label):
    if not path.exists():
        print(f"Downloading {label}...")
        urllib.request.urlretrieve(url, path)


def ensure_assets():
    FONTS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    download_if_missing(FONTS_DIR / "Roboto-Regular.ttf", ROBOTO_URL,      "Roboto-Regular.ttf")
    download_if_missing(FONTS_DIR / "Roboto-Bold.ttf",    ROBOTO_BOLD_URL, "Roboto-Bold.ttf")
    download_if_missing(MODELS_DIR / "face_detector.tflite",  DETECTOR_URL,   "face_detector.tflite")
    download_if_missing(MODELS_DIR / "face_landmarker.task",  LANDMARKER_URL, "face_landmarker.task")


def _fallback(size):
    for path in ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def load_fonts():
    def load(name, size):
        try:
            return ImageFont.truetype(str(FONTS_DIR / name), size)
        except OSError:
            return _fallback(size)
    return {
        "sm":   load("Roboto-Regular.ttf", 15),
        "reg":  load("Roboto-Regular.ttf", 18),
        "bold": load("Roboto-Bold.ttf",    20),
        "big":  load("Roboto-Bold.ttf",    28),
    }
