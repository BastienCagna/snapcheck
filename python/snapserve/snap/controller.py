from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from lepton.session.controller import CRUDRouter, SessionStore, get_session_from_token
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


class SnapRouter(CRUDRouter):
    # Créer AbstractCRUDRouter(APIRouter) et FileCRUDRouter(AbstractCRUDRouter)
    def __init__(self, store: SessionStore):
        super().__init__(store)
        self.add_api_route("/{snap_id}/image/{src:path}", self.get_image, methods=["GET"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.export_as_html, methods=["GET"])
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.export_as_pdf, methods=["GET"])
        self.add_api_route("/{snap_id}/field", self.update_field, methods=["PATCH"], response_model=LightweightResponse)

    def get_image(self, snap_id: str, src: str, session=Depends(get_session_from_token)):
        # TODO: check the session ?

        item = self.store.get_by_id(snap_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Snap not found")

        # Reject missing src to avoid serving the directory itself
        normalized_src = src.lstrip("/")
        if not normalized_src:
            raise HTTPException(status_code=404, detail="Image not found")

        image_path = op.join(item.object._dir.name, normalized_src)
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

    def export_as_html(self, snap_id: str, path: str):
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.snap.export_to_html(path)
        print("Export:", path)

    def export_as_pdf(self, snap_id: str, path: str):
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.snap.export_to_pdf(path)
        print("Export:", path)

    def update_field(self, snap_id: str, update: FieldUpdateRequest):
        """
        Update a specific field of a snap with version conflict detection.

        Args:
            snap_id: Snap ID
            update: Field update request with field_path, value, and optional expected_version

        Returns:
            Lightweight response with version and status

        Raises:
            409: Version conflict (expected_version doesn't match current)
            404: Snap not found
            400: Invalid field path
        """
        item = self.store.get_by_id(snap_id)
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

        return LightweightResponse(
            ok=True, version=item.version, has_changed=item.snap._has_changed, timestamp=time.time()
        )
