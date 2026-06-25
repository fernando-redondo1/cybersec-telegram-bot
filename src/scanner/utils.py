import csv
import os
import sys
import threading
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .constants import SNAPSHOTS_DIR, LOGS_DIR

if sys.platform == "win32":
    import winsound


def tw(font, text):
    bb = font.getbbox(text)
    return bb[2] - bb[0]


def pil_text(frame: np.ndarray, items: list) -> np.ndarray:
    img  = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    for text, pos, font, c in items:
        draw.text(pos, text, font=font, fill=(c[2], c[1], c[0]))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def find_cameras(limit=4):
    cams = []
    for i in range(limit):
        c = cv2.VideoCapture(i)
        if c.isOpened():
            cams.append(i)
        c.release()
    return cams or [0]


def beep():
    if sys.platform == "win32":
        threading.Thread(target=lambda: winsound.Beep(1000, 150), daemon=True).start()
    elif sys.platform == "darwin":
        threading.Thread(target=lambda: os.system("afplay /System/Library/Sounds/Ping.aiff"), daemon=True).start()
    else:
        threading.Thread(target=lambda: os.system(
            "paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null"
            " || aplay -q /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null"
            " || printf '\\a'"
        ), daemon=True).start()


def save_snapshot(frame: np.ndarray):
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    p  = SNAPSHOTS_DIR / f"face_{ts}.jpg"
    cv2.imwrite(str(p), frame)
    return p


def log_attendance(count: int):
    LOGS_DIR.mkdir(exist_ok=True)
    p   = LOGS_DIR / f"attendance_{datetime.now().strftime('%Y%m%d')}.csv"
    new = not p.exists()
    with open(p, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "face_count"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count])


def draw_corners(frame, x, y, w, h, color, t=3):
    cs = max(14, min(w, h) // 5)
    for px, py, sx, sy in [(x, y, 1, 1), (x+w, y, -1, 1),
                            (x, y+h, 1, -1), (x+w, y+h, -1, -1)]:
        cv2.line(frame, (px, py), (px + sx*cs, py), color, t, cv2.LINE_AA)
        cv2.line(frame, (px, py), (px, py + sy*cs), color, t, cv2.LINE_AA)
