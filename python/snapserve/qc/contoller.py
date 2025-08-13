from fastapi import APIRouter, Depends, HTTPException
from snapcheck.qc.io import load_quality_control
from snapserve.qc.models import NoteModel, QualityControlModel
from fastapi.responses import FileResponse
import os.path as op


router = APIRouter()

qc = load_quality_control(op.join(op.dirname(__file__), "..", "..", "..", ".local/demo.snpk"))

def get_qc_data():
    ret_qc = qc.to_dict(compress=False)
    ret_qc["filename"] = op.split(qc._path)[1] if qc._path else None
    ret_qc["has_changed"] = qc._has_changed or False
    ret_qc["is_cancellable"] = len(qc._backups) > 0
    ret_qc["is_redoable"] = len(qc._forups) > 0
    return ret_qc

@router.get("/", response_model=QualityControlModel)
def get_full_qc():
    return get_qc_data()


@router.get("/image/{src:path}", response_class=FileResponse)
def get_image(src: str):
    image_path = op.join(qc._dir.name, src)
    if not op.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path, media_type="image/png")


@router.put("/note")
def update_note(note: NoteModel, response_model=QualityControlModel):
    if not qc:
        raise HTTPException(status_code=404, detail="Quality control not found")
    qc.update_note(note)
    return get_qc_data()