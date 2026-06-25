# Face Scanner

I built this to get a feel for real-time computer vision without relying on cloud APIs. The goal was to keep everything running locally — models downloaded once, no data leaving the machine.

It detects faces from a webcam feed, draws corner brackets around each one, and lets you toggle a 478-point mesh overlay, blur faces for privacy demos, record video, and log detections to CSV. Optional age/gender analysis runs in a background thread so it never blocks the main feed.

---

## Features

- **Real-time face detection** — MediaPipe BlazeFace short-range model, runs at 30+ fps on CPU
- **Face mesh** — 478-landmark overlay, toggled live with `M`
- **Face blur** — Gaussian blur over each detected face (toggle with `B`); useful for demos
- **Video recording** — save an `.avi` clip at any time (`R` to start/stop)
- **Snapshot capture** — save the current frame as a `.jpg` (`S`)
- **Attendance log** — appends a timestamped row to a CSV every time a new face appears
- **Age / gender** (optional) — installs `deepface` to enable; runs async so it never drops frames
- **Multi-camera** — cycles through all connected cameras with `C`
- **Fullscreen** — `F` toggles; restores to 1280×720 on exit
- **Roboto HUD** — font downloaded automatically on first run

---

## Tech Stack

| Tool | Why |
|------|-----|
| **MediaPipe Tasks API** | BlazeFace + FaceLandmarker, ~1 MB combined, CPU-only |
| **OpenCV** | Camera capture, drawing, video writing |
| **Pillow** | Roboto TTF rendering on NumPy frames |
| **deepface** *(optional)* | Age/gender analysis — ~500 MB TensorFlow install |

---

## Quickstart

```bash
pip install -r requirements.txt
python main.py
```

Models and fonts download automatically on first run (~2 MB total, no account needed).

To enable age/gender analysis:
```bash
pip install deepface
python main.py
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `S` | Save snapshot |
| `R` | Start / stop recording |
| `B` | Toggle face blur |
| `M` | Toggle 478-point mesh |
| `C` | Cycle to next camera |
| `F` | Toggle fullscreen |
| `Q` / `Esc` | Quit |

The window's close button also works.

---

## Output Files

Everything stays local:

```
snapshots/    # JPEG captures (face_YYYYMMDD_HHMMSS.jpg)
recordings/   # AVI clips     (rec_YYYYMMDD_HHMMSS.avi)
logs/         # CSV logs       (attendance_YYYYMMDD.csv)
models/       # TFLite models  (downloaded once)
fonts/        # Roboto TTF     (downloaded once)
```

None of these directories are committed — see `.gitignore`.

---

## Docker

```bash
docker build -t face-scanner .

# Linux — pass the webcam and X11 socket for the GUI
docker run --device=/dev/video0 \
           -e DISPLAY=$DISPLAY \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           face-scanner
```

> **Windows/Mac:** Docker Desktop doesn't expose USB webcams or X11. Run locally with `python main.py` on those platforms.

---

## Requirements

```
python >= 3.9
opencv-python >= 4.8
mediapipe >= 0.10
numpy >= 1.24
Pillow >= 10.0
```

Sound alert works on Windows (`winsound`), macOS (`afplay`), and Linux (`paplay`/`aplay`).

---

## Project Structure

```
face-scanner/
├── main.py                  # entry point
├── Dockerfile
├── requirements.txt
└── src/
    └── scanner/
        ├── app.py           # main loop and key bindings
        ├── assets.py        # model/font downloads
        ├── analysis.py      # optional age/gender background thread
        ├── utils.py         # helpers: beep, snapshot, attendance log, HUD drawing
        └── constants.py     # paths, URLs, colours
```
