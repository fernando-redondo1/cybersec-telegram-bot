import time
from datetime import datetime

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision

from .constants import (WIN_NAME, MODELS_DIR, RECORDINGS_DIR,
                         C_GREEN, C_RED, C_CYAN, C_WHITE, C_BG, C_YELLOW)
from .assets import ensure_assets, load_fonts
from .analysis import _DEEPFACE, _lock, _queue, _cache
from .utils import tw, pil_text, find_cameras, beep, save_snapshot, log_attendance, draw_corners


def main():
    ensure_assets()
    fonts = load_fonts()

    RunningMode = mp_vision.RunningMode

    face_det = mp_vision.FaceDetector.create_from_options(
        mp_vision.FaceDetectorOptions(
            base_options=mp_tasks.BaseOptions(
                model_asset_path=str(MODELS_DIR / "face_detector.tflite")),
            running_mode=RunningMode.IMAGE,
            min_detection_confidence=0.5,
        ))

    face_mesh = mp_vision.FaceLandmarker.create_from_options(
        mp_vision.FaceLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(
                model_asset_path=str(MODELS_DIR / "face_landmarker.task")),
            running_mode=RunningMode.IMAGE,
            num_faces=10,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        ))

    cameras = find_cameras()
    cam_idx = 0

    def open_cam(idx):
        c = cv2.VideoCapture(cameras[idx])
        c.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        c.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return c

    cap = open_cam(0)
    cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN_NAME, 1280, 720)

    fullscreen = show_mesh = blur_mode = recording = False
    writer     = None
    prev_time  = time.time()
    prev_faces = 0
    last_anal  = 0.0
    notif      = ""
    notif_t    = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        fh_full, fw_full = frame.shape[:2]
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        det_res = face_det.detect(mp_img)
        faces   = []
        if det_res.detections:
            for d in det_res.detections:
                bb = d.bounding_box
                fx = max(0, bb.origin_x)
                fy = max(0, bb.origin_y)
                fw = min(bb.width,  fw_full - fx)
                fh = min(bb.height, fh_full - fy)
                if fw > 0 and fh > 0:
                    faces.append((fx, fy, fw, fh))

        n = len(faces)

        if n > 0 and prev_faces == 0:
            beep()
            log_attendance(n)
        if n == 0:
            with _lock:
                _cache.clear()
        prev_faces = n

        if _DEEPFACE and faces and time.time() - last_anal > 2.0:
            last_anal = time.time()
            with _lock:
                _queue.clear()
                for i, (fx, fy, fw, fh) in enumerate(faces):
                    _queue.append((i, frame[fy:fy+fh, fx:fx+fw].copy()))

        mesh_res = face_mesh.detect(mp_img) if show_mesh else None

        for fx, fy, fw, fh in faces:
            if blur_mode:
                frame[fy:fy+fh, fx:fx+fw] = cv2.GaussianBlur(
                    frame[fy:fy+fh, fx:fx+fw], (55, 55), 30)
            else:
                draw_corners(frame, fx, fy, fw, fh, C_GREEN)

        if mesh_res and mesh_res.face_landmarks:
            for face_lms in mesh_res.face_landmarks:
                for lm in face_lms:
                    cv2.circle(frame,
                               (int(lm.x * fw_full), int(lm.y * fh_full)),
                               1, C_CYAN, -1)

        now = time.time()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now

        ov = frame.copy()
        cv2.rectangle(ov, (0, 0), (fw_full, 52), C_BG, -1)
        cv2.rectangle(ov, (0, fh_full - 42), (fw_full, fh_full), C_BG, -1)
        cv2.addWeighted(ov, 0.65, frame, 0.35, 0, frame)

        if recording:
            cv2.circle(frame, (fw_full - 22, 26), 9, C_RED, -1, cv2.LINE_AA)

        badge = f"Faces: {n}"
        bw    = tw(fonts["bold"], badge)
        cx    = fw_full // 2
        cv2.rectangle(frame, (cx - bw//2 - 10, 8), (cx + bw//2 + 10, 46),
                      C_GREEN if n > 0 else C_RED, -1)

        fps_s = f"FPS: {fps:.1f}"
        hint  = ("[S]Cap [R]STOP [B]Blur [M]Mesh [C]Cam [F]Full [Q]Quit"
                 if recording else
                 "[S]Cap [R]Rec  [B]Blur [M]Mesh [C]Cam [F]Full [Q]Quit")

        items = [
            ("FACE SCANNER",  (12, 12),                                      fonts["big"],  C_GREEN),
            (fps_s,           (fw_full - tw(fonts["bold"], fps_s) - 12, 16), fonts["bold"], C_CYAN),
            (badge,           (cx - bw//2, 16),                              fonts["bold"], C_BG),
            (hint,            (12, fh_full - 32),                            fonts["sm"],   C_WHITE),
        ]

        if _DEEPFACE:
            with _lock:
                cache = dict(_cache)
            for i, (fx, fy, fw, fh) in enumerate(faces):
                if i in cache:
                    age, gen = cache[i]
                    items.append((f"{gen} ~{age}y", (fx, max(4, fy - 26)),
                                  fonts["reg"], C_YELLOW))

        if notif and time.time() - notif_t < 2.5:
            items.append((notif, (12, fh_full - 60), fonts["bold"], C_GREEN))

        frame = pil_text(frame, items)

        if recording and writer:
            writer.write(frame)

        cv2.imshow(WIN_NAME, frame)

        # waitKey processes window events — check window state after, not before
        key = cv2.waitKey(1) & 0xFF

        try:
            if cv2.getWindowProperty(WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break

        if key in (ord("q"), 27):
            break
        elif key == ord("s"):
            notif   = f"Saved: {save_snapshot(frame).name}" if n > 0 else "No faces detected"
            notif_t = time.time()
        elif key == ord("r"):
            if not recording:
                RECORDINGS_DIR.mkdir(exist_ok=True)
                ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
                rpath = str(RECORDINGS_DIR / f"rec_{ts}.avi")
                writer    = cv2.VideoWriter(rpath, cv2.VideoWriter_fourcc(*"XVID"), 20.0, (fw_full, fh_full))
                recording = True
                notif     = f"REC started: rec_{ts}.avi"
            else:
                recording = False
                if writer:
                    writer.release()
                    writer = None
                notif = "Recording stopped"
            notif_t = time.time()
        elif key == ord("b"):
            blur_mode = not blur_mode
            notif     = "Blur: ON" if blur_mode else "Blur: OFF"
            notif_t   = time.time()
        elif key == ord("m"):
            show_mesh = not show_mesh
            notif     = "Mesh: ON" if show_mesh else "Mesh: OFF"
            notif_t   = time.time()
        elif key == ord("c"):
            cam_idx = (cam_idx + 1) % len(cameras)
            cap.release()
            cap     = open_cam(cam_idx)
            notif   = f"Camera {cameras[cam_idx]}"
            notif_t = time.time()
        elif key == ord("f"):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(WIN_NAME, 1280, 720)

    if writer:
        writer.release()
    cap.release()
    face_det.close()
    face_mesh.close()
    cv2.destroyAllWindows()
