from typing import List
from fastapi import APIRouter, HTTPException
from snapserve.snap.models import SnapModel, SnapCheckSessionModel
from fastapi.responses import FileResponse
import os.path as op
import mimetypes

from snapserve.snap.store import SnapStore
from snapserve.app_data import APP_DATA

router = APIRouter()

snap_store = SnapStore()

@router.post("/session", response_model=SnapCheckSessionModel)
def create_session():
    return snap_store.new_session()

@router.post("/{sid}", response_model=SnapCheckSessionModel)
def get_session_infos(sid: str):
    return snap_store.get_session(sid)

@router.get("/{sid}/saveall", response_model=SnapModel)
def save_all_snaps(sid: str):
    sess = snap_store.get_session(sid)
    for item in sess.items:
        item.save()
    return [item.to_dict() for item in sess.items]

@router.get("/{sid}/close", response_model=List[SnapModel] | None)
def close_session(sid: str):
    items = snap_store.close_session(sid)
    if items:
        return [item.to_dict() for item in items]
    return None

@router.get("/{sid}/list", response_model=List[SnapModel])
def list_qc(sid: str):
    # TODO: use sid
    return [item.to_dict() for item in snap_store.get_all()]

@router.get("/{sid}/open/{path:path}", response_model=SnapModel)
def open_snap(sid: str, path: str):
    # TODO: implent and also use sid
    item = snap_store.open(sid, path)
    APP_DATA.add_to_history(path)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    return item.to_dict()

@router.get("/{sid}/{snapid}/save", response_model=SnapModel)
def save_snap(sid: str, snapid: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.save()
    return item.to_dict()

@router.get("/{sid}/{snapid}/saveas", response_model=SnapModel)
def save_snap_as(sid: str, snapid: str, path: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.save(path)
    return item.to_dict()


@router.get("/{sid}/{snapid}/image/{src:path}")
def get_image(sid: str, snapid: str, src: str):
    # TODO: validate sid/session ownership
    item = snap_store.get_by_id(snapid)
    if item is None:
        raise HTTPException(status_code=404, detail="Snap not found")

    # Reject missing src to avoid serving the directory itself
    normalized_src = src.lstrip("/")
    if not normalized_src:
        raise HTTPException(status_code=404, detail="Image not found")

    image_path = op.join(item.snap._dir.name, normalized_src)
    if not op.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    return FileResponse(
        image_path,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{op.basename(image_path)}"'
        }
    )


@router.put("/{sid}/{snapid}/rating/{ratingId}/{value}")
def update_rating(sid: str, snapid: str, ratingId: str, value: float):
    # TODO: use sid
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.update_rating(ratingId, value)
    return item.to_dict()