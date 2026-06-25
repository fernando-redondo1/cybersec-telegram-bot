from pathlib import Path

WIN_NAME       = "Face Scanner"
SNAPSHOTS_DIR  = Path("snapshots")
RECORDINGS_DIR = Path("recordings")
LOGS_DIR       = Path("logs")
FONTS_DIR      = Path("fonts")
MODELS_DIR     = Path("models")

ROBOTO_URL      = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
ROBOTO_BOLD_URL = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
DETECTOR_URL    = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
LANDMARKER_URL  = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"

C_GREEN  = (  0, 255, 120)
C_RED    = (  0,  60, 255)
C_CYAN   = (255, 220,   0)
C_WHITE  = (255, 255, 255)
C_BG     = ( 20,  20,  20)
C_YELLOW = (  0, 200, 255)
