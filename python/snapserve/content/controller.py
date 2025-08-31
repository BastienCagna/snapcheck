from typing import List
from fastapi import APIRouter, Depends, HTTPException
import os.path as op

from snapserve.content.models import ContentModel

CONTENT_DIR = op.abspath(op.join(__file__, "..", "..", "..", "..", "shared", "static_content"))

router = APIRouter()

@router.get("/{path:path}", response_model=ContentModel)
def get_static_content(path: str) -> ContentModel:
    f = op.join(CONTENT_DIR, path)
    if not op.isfile(f):
        raise HTTPException(status_code=404, detail="File not found")

    with open(f, "r") as file:
        content = file.read()

    return ContentModel(path=path, content=content)

