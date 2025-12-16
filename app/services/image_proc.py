import io
import time
import base64
import secrets
import re
from pathlib import Path
from typing import Tuple

from PIL import Image
from fastapi.concurrency import run_in_threadpool

# Base directory
BASE_UPLOAD_DIR = Path("uploads") 

def sanitize_filename(name: str) -> str:
    """
    Sanitizes a string to be safe for directory names.
    Example: "Skin Issue" -> "skin_issue", "Warts!" -> "warts"
    """
   
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    
    clean_name = re.sub(r'_+', '_', clean_name)
    return clean_name.strip('_').lower()

async def save_image_to_disk(image_bytes: bytes, original_filename: str, subfolder: str = "") -> Tuple[str, str]:
    """
    Saves image to uploads/{subfolder}/{unique_name}.
    Creates the directory structure if it doesn't exist.
    """
    suffix = Path(original_filename).suffix if original_filename else '.jpg'
    if len(suffix) > 5 or suffix.lower() not in ['.png', '.jpg', '.jpeg']:
        suffix = '.jpg' 

    
    target_dir = BASE_UPLOAD_DIR / subfolder
    
   
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    unique_filename = f"{secrets.token_urlsafe(8)}_{int(time.time())}{suffix.lower()}"
    file_path = target_dir / unique_filename

    
    await run_in_threadpool(file_path.write_bytes, image_bytes)

    server_url_path = f"/static/{subfolder}/{unique_filename}".replace("//", "/")
    
    return unique_filename, server_url_path


def normalize_image_bytes(image_bytes: bytes, max_side: int = 1024) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")

    w, h = img.size
    mx = max(w, h)
    if mx > max_side:
        scale = float(max_side) / mx
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70, optimize=True)
    return buf.getvalue()

def encode_image_to_base64_datauri(image_bytes: bytes, filename_hint: str = "image.jpg") -> str:
    ext = Path(filename_hint).suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"