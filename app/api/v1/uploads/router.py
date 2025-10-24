from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
import os
import shutil
import uuid
from app.core.security import get_current_user
from app.services.file_storage import save_uploaded_image

router = APIRouter(prefix="/upload", tags=["uploads"])
MEDIA_DIR = "app/media"


@router.post("/save")
async def save_file(file: UploadFile = File(...),user=Depends(get_current_user)):

    saved = await save_uploaded_image(
        file
    )  #! delegamos la logica en save_upload_image para que la ruta quede limpia
    # return {
    #     "filename":saved["filename"],
    #     "content_type":saved["content_type"],
    #     "url": saved["url"]"
    # }

    return {
        "filename": saved["filename"],
        "conten_type": saved["content_type"],
        "url": saved["url"],
        "size": saved["size"],
        # "chunk_size_used": saved["chunk_size_used"],
        # "chunk_calls": saved["chunk_calls"],
        # "chunk_sizes_sample": saved["chunk_sizes_sample"],
    }

    # print(f"saved {saved}")
    return saved
