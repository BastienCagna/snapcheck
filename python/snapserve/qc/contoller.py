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


@router.get("/image", response_class=FileResponse)
def get_image():
    image_path = op.join(".local/demo_snapcheck", qc.boards[0].elements[0]['src']) # TODO: enhance te file reading to get proper element objects and not dicts
    return FileResponse(image_path, media_type="image/png")