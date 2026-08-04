from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os.path as op
import mimetypes
from lepton.session.controller import CRUDRouter, SessionStore, get_session_from_token
from tempfile import TemporaryDirectory

from snapcheck.snap.snap import Snap

router = APIRouter()


class SnapRouter(CRUDRouter):
    def __init__(self, store: SessionStore):
        super().__init__(store)
        self.add_api_route("/{snap_id}/image/{src:path}", self.get_image, methods=["GET"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.export_as_html, methods=["POST"])
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.export_as_pdf, methods=["POST"])
        self.add_api_route("/{snap_id}/html/{path:path}", self.download_as_html, methods=["GET"], response_class=FileResponse)
        self.add_api_route("/{snap_id}/pdf/{path:path}", self.download_as_pdf, methods=["GET"], response_class=FileResponse)


    def get_image(self, snap_id: str, src: str, session=Depends(get_session_from_token)):
        # TODO: check the session ?

        item = self.store.get_by_id(snap_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Snap not found")

        # Reject missing src to avoid serving the directory itself
        normalized_src = src.lstrip("/")
        if not normalized_src:
            raise HTTPException(status_code=404, detail="Image not found")

        if item.object._dir:
            image_path = op.join(item.object._dir.name, normalized_src)
        else:
            # If the snap is not saved yet
            image_path = src
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
        item.object.export_to_html(Path(path))

    def export_as_pdf(self, snap_id: str, path: str):
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        item.object.export_to_pdf(Path(path))

    def download_as_html(self, snap_id: str):
        """ Export as HTML in a temporary directory, zip and return the path to the zip file """
        temp_dir = TemporaryDirectory(prefix="snapserve_export_")
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        snap: Snap = item.object
        export_path = Path(temp_dir.name) / Path(snap._filepath).stem
        zip_path = snap.export_to_html(export_path, compress=True)
        print("HTML exported to:", zip_path)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{op.basename(zip_path)}"'},
        )

    def download_as_pdf(self, snap_id: str):
        """ Export as PDF in a temporary directory and return the path to the PDF file """
        temp_dir = TemporaryDirectory(prefix="snapserve_export_")
        item = self.store.get_by_id(snap_id)
        if not item:
            raise HTTPException(status_code=404, detail="Snap not found")
        snap: Snap = item.object
        export_path = Path(temp_dir.name) / f"{Path(snap._filepath).stem}.pdf"
        snap.export_to_pdf(export_path)
        print("PDF exported to:", export_path)
        return FileResponse(
            export_path,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{op.basename(export_path)}"'},
        )