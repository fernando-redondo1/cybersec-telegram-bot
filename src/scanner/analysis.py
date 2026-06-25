import threading
import time

_lock  = threading.Lock()
_queue = []
_cache = {}

try:
    from deepface import DeepFace as _DF
    _DEEPFACE = True
except ImportError:
    _DEEPFACE = False


def _worker():
    while True:
        task = None
        with _lock:
            if _queue:
                task = _queue.pop(0)
        if task is None:
            time.sleep(0.05)
            continue
        idx, img = task
        try:
            res = _DF.analyze(img, actions=["age", "gender"],
                              enforce_detection=False, silent=True)
            if isinstance(res, list):
                res = res[0]
            with _lock:
                _cache[idx] = (int(res.get("age", 0)),
                               res.get("dominant_gender", "?")[0].upper())
        except Exception:
            pass


if _DEEPFACE:
    threading.Thread(target=_worker, daemon=True).start()
