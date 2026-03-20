from fastapi import APIRouter, UploadFile, File, Form
from uuid import uuid4
import os
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("")
async def create_post(
    image: UploadFile = File(...),
    description: str = Form("")
):
    post_id = str(uuid4())

    file_ext = image.filename.split(".")[-1]
    filename = f"{post_id}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await image.read())

    return {
        "id": post_id,
        "image_url": f"http://127.0.0.1:8000/uploads/{filename}",
        "description": description,
        "interest_count": 0
    }
