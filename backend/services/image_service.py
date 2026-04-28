"""OutfitCheck AI - Image Processing Service"""
import os
import uuid
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO
from backend.config import UPLOAD_DIR


def save_uploaded_image(file_bytes: bytes, filename: str) -> str:
    """
    Save an uploaded image and return the relative URL path.
    Resizes to max 800px for storage efficiency.
    """
    # Generate unique filename
    ext = Path(filename).suffix.lower() or ".jpg"
    unique_name = f"{uuid.uuid4()}{ext}"
    filepath = UPLOAD_DIR / unique_name

    # Process and resize image
    try:
        img = Image.open(BytesIO(file_bytes))

        # Convert RGBA to RGB if needed
        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background

        # Resize if too large (max 800px on longest side)
        max_size = 800
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)

        img.save(filepath, quality=85)
    except Exception:
        # If PIL fails, save raw bytes
        with open(filepath, "wb") as f:
            f.write(file_bytes)

    return f"/uploads/{unique_name}"


def image_to_base64(file_bytes: bytes) -> str:
    """Convert image bytes to base64 string for AI APIs."""
    return base64.b64encode(file_bytes).decode("utf-8")


def delete_image(image_url: str) -> bool:
    """Delete an image file from storage."""
    if not image_url:
        return False

    filename = image_url.split("/")[-1]
    filepath = UPLOAD_DIR / filename

    try:
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception:
        pass

    return False
