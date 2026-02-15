from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from snapserve.snap.models import SnapModel, SnapCheckSessionModel
from fastapi.responses import FileResponse
import os.path as op
import mimetypes
import time


router = APIRouter()



# Pydantic models for request/response
class FieldUpdateRequest(BaseModel):
    """Request model for partial field update"""

    field_path: str  # e.g., "metadata.title" or "boards.0.description"
    value: Any
    expected_version: Optional[int] = None


class LightweightResponse(BaseModel):
    """Lightweight response for modifications"""

    ok: bool
    version: int
    has_changed: bool
    timestamp: float


@router.get("/{sid}/open/{path:path}", response_model=SnapModel)
def open_snap(sid: str, path: str):
    # TODO: implent and also use sid
    item = snap_store.open(sid, path)
    APP_DATA.add_to_history(path)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    return item.to_dict(clean=True)


@router.get("/{sid}/{snapid}/close", response_model=None)
def close_snap(sid: str, snapid: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    snap_store.close(sid, snapid)
    return None


@router.get("/{sid}/{snapid}/save", response_model=SnapModel)
def save_snap(sid: str, snapid: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.save()
    return item.to_dict(clean=True)


@router.get("/{sid}/{snapid}/saveas", response_model=SnapModel)
def save_snap_as(sid: str, snapid: str, path: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.save(path)
    return item.to_dict(clean=True)


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
        headers={"Content-Disposition": f'inline; filename="{op.basename(image_path)}"'},
    )


@router.get("/{sid}/{snapid}/html/{path:path}")
def export_as_html(sid: str, snapid: str, path: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.export_to_html(path)
    print("Export:", path)


@router.get("/{sid}/{snapid}/pdf/{path:path}")
def export_as_pdf(sid: str, snapid: str, path: str):
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")
    item.snap.export_to_pdf(path)
    print("Export:", path)


@router.patch("/{sid}/{snapid}/field", response_model=LightweightResponse)
def update_field(sid: str, snapid: str, update: FieldUpdateRequest):
    """
    Update a specific field of a snap with version conflict detection.

    Args:
        sid: Session ID
        snapid: Snap ID
        update: Field update request with field_path, value, and optional expected_version

    Returns:
        Lightweight response with version and status

    Raises:
        409: Version conflict (expected_version doesn't match current)
        404: Snap not found
        400: Invalid field path
    """
    # TODO: use sid
    item = snap_store.get_by_id(snapid)
    if not item:
        raise HTTPException(status_code=404, detail="Snap not found")

    # Check version conflict
    if update.expected_version is not None and update.expected_version != item.version:
        raise HTTPException(
            status_code=409, detail=f"Version conflict: expected {update.expected_version}, current {item.version}"
        )

    # Update the field using dot notation
    try:
        parts = update.field_path.split(".")
        obj = item.snap

        # Navigate to parent object
        for part in parts[:-1]:
            # Handle array indices
            if part.isdigit():
                obj = obj[int(part)]
            # Handle filtering by id in lists
            if part.startswith("{") and part.endswith("}"):
                # e.g., {id:ratingId}
                key, val = part[1:-1].split(":", 1)
                obj = next((o for o in obj if getattr(o, key) == val), None)
                if obj is None:
                    raise HTTPException(status_code=400, detail=f"Invalid field path: {update.field_path}")
            else:
                obj = getattr(obj, part)

        # Set the final value
        final_key = parts[-1]
        if final_key.isdigit():
            idx = int(final_key)
            if idx < 0 or idx >= len(obj):
                raise HTTPException(status_code=400, detail=f"Invalid field path: {update.field_path}")
            if obj[idx] != update.value:
                obj[idx] = update.value
                item.snap._has_changed = True
        else:
            if hasattr(obj, final_key) and getattr(obj, final_key) != update.value:
                setattr(obj, final_key, update.value)
                item.snap._has_changed = True

    except (AttributeError, IndexError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid field path: {update.field_path}")

    item.increment_version()

    return LightweightResponse(ok=True, version=item.version, has_changed=item.snap._has_changed, timestamp=time.time())
