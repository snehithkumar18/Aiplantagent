from typing import Tuple

Box = Tuple[int, int, int, int]


def crop_leaf(image_path: str, box: Box):
    """
    Crop the image using the bounding box.

    box format: (x1, y1, x2, y2)
    Returns the cropped leaf image (numpy array, BGR).
    """
    try:
        import cv2  # type: ignore
    except Exception as e:
        raise ImportError("opencv-python is required for crop_leaf(). Install it with pip.") from e

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image is corrupted or unreadable")

    h, w = img.shape[:2]
    x1, y1, x2, y2 = box

    # Clamp to image bounds
    x1 = max(0, min(int(x1), w - 1))
    x2 = max(0, min(int(x2), w))
    y1 = max(0, min(int(y1), h - 1))
    y2 = max(0, min(int(y2), h))

    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid crop box")

    cropped = img[y1:y2, x1:x2]
    if cropped.size == 0:
        raise ValueError("Empty crop result")

    return cropped

