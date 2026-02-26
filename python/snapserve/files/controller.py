from typing import List
from fastapi import APIRouter, Depends, HTTPException
from lepton.utils import get_lepton_app
from snapserve.files.models import DirectoryItemModel, DirectoryModel
import os.path as op
from os import listdir

router = APIRouter()


@router.get("/{path:path}", response_model=DirectoryModel)
@router.get("/", response_model=DirectoryModel)
def list_directory(path: str = None, extensions: List[str]|None = None, app=Depends(get_lepton_app)):
    if path is None:
        path = app.settings.get("files.default_path").value

    if not op.isdir(path):
        raise HTTPException(status_code=404, detail="Directory not found")

    dirs = []
    files = []
    for item in sorted(listdir(path)):
        if op.isdir(op.join(path, item)):
            dirs.append(item)
        elif extensions is not None:
            _, ext = op.split(item)
            if ext in extensions:
                files.append(item)
        else:
            files.append(item)

    content = list(DirectoryItemModel(
        path=op.join(path, item),
        filename=item,
        isdir=op.isdir(op.join(path, item))
    ) for item in dirs + files)

    directory = DirectoryModel(
        path=path,
        content=content,
        parent=op.realpath(op.join(path, '..')) if path != '/' else None
    )

    return directory
