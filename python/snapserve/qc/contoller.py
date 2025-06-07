from fastapi import APIRouter, Depends, HTTPException
from snapcheck.qc.io import load_quality_control
from snapserve.qc.models import QualityControlModel
from fastapi.responses import FileResponse
import os.path as op


router = APIRouter()

qc = load_quality_control(op.join(op.dirname(__file__), "..", "..", "..", ".local/demo_snapcheck.json"))

@router.get("/", response_model=QualityControlModel)
def get_full_qc():
    return qc.__dict__


@router.get("/image/{src}", response_class=FileResponse)
def get_image(src: str):
    print(f"request image: {src}")
    image_path = op.join(".local/demo_snapcheck", src)  # Assumes 'src' is passed directly as a valid path segment
    if not op.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/png")