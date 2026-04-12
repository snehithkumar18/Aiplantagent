import logging
import threading
from typing import Optional, Tuple

from plant_detector_model import load_plant_detector

logger = logging.getLogger(__name__)

Box = Tuple[int, int, int, int]

_MODEL_LOCK = threading.Lock()
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        _MODEL = load_plant_detector()
        return _MODEL


def detect_plant_detailed(
    image_path: str, confidence_threshold: float = 0.5
) -> Tuple[str, Optional[Box], Optional[str]]:
    """
    Detailed plant detection with status:

    Returns:
      - ("detected", box, None)
      - ("not_detected", None, None)
      - ("failed", None, error_message)
    """
    logger.info("Plant detection started: %s", image_path)

    try:
        try:
            import cv2  # type: ignore
        except Exception as e:
            msg = f"OpenCV not available: {type(e).__name__}"
            logger.exception(msg)
            return "failed", None, msg

        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            logger.warning("Plant detection rejected unreadable/corrupt image: %s", image_path)
            return "not_detected", None, None

        try:
            model = _get_model()
        except Exception as e:
            msg = f"YOLO model load failed: {type(e).__name__}: {e}"
            logger.exception(msg)
            return "failed", None, msg

        results = model.predict(img_bgr, verbose=False)
        if not results:
            logger.info("Plant detection: no results returned")
            return "not_detected", None, None

        r0 = results[0]
        boxes = getattr(r0, "boxes", None)
        if boxes is None or len(boxes) == 0:
            logger.info("Plant detection: no bounding boxes detected")
            return "not_detected", None, None

        best = None  # (conf, x1,y1,x2,y2)
        for b in boxes:
            conf = float(
                getattr(b, "conf", [0.0])[0]
                if hasattr(getattr(b, "conf", None), "__len__")
                else getattr(b, "conf", 0.0)
            )
            if conf < confidence_threshold:
                continue

            xyxy = getattr(b, "xyxy", None)
            if xyxy is None or len(xyxy) == 0:
                continue

            x1, y1, x2, y2 = [int(v) for v in xyxy[0].tolist()]
            if best is None or conf > best[0]:
                best = (conf, x1, y1, x2, y2)

        if best is None:
            logger.info("Plant detection: all detections below threshold=%.2f", confidence_threshold)
            return "not_detected", None, None

        _, x1, y1, x2, y2 = best
        box: Box = (x1, y1, x2, y2)
        logger.info("Plant detected with box=%s", box)
        return "detected", box, None

    except Exception as e:
        msg = f"YOLO inference failed: {type(e).__name__}: {e}"
        logger.exception("Plant detection failed: %s", e)
        return "failed", None, msg


def detect_plant(image_path: str, confidence_threshold: float = 0.5) -> Tuple[bool, Optional[Box]]:
    """
    Detect whether an image contains a plant leaf.

    Returns:
      - (False, None) if no valid detections
      - (True, (x1, y1, x2, y2)) for the best detection
    """
    status, box, _err = detect_plant_detailed(image_path, confidence_threshold=confidence_threshold)
    if status == "detected" and box is not None:
        return True, box
    return False, None

