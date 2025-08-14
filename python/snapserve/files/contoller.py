from fastapi import APIRouter, Depends, HTTPException
from snapcheck.qc.io import load_quality_control
from snapserve.files.models import DirectoryItemModel, DirectoryModel
from snapserve.qc.models import NoteModel, QualityControlModel
from fastapi.responses import FileResponse
import os.path as op
from os import listdir, getcwd

router = APIRouter()

@router.get("/{path:path}", response_model=DirectoryModel)
@router.get("/", response_model=DirectoryModel)
def list_directory(path: str = None):
    if path is None:
        path = getcwd() #op.expanduser("~")  # Default to home directory

    if not op.isdir(path):
        raise HTTPException(status_code=404, detail="Directory not found")

    items = sorted(listdir(path))
    content = list(DirectoryItemModel(
        path=op.join(path, item),
        filename=item,
        isdir=op.isdir(op.join(path, item))
    ) for item in items)

    directory = DirectoryModel(
        path=path,
        content=content,
        parent=op.realpath(op.join(path, '..')) if path != '/' else None
    )

    return directory
