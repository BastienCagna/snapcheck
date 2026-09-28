from typing import List
from fastapi import APIRouter, Depends, HTTPException
import os.path as op

from snapserve.content.models import ContentModel

CONTENT_DIR = op.abspath(op.join(op.dirname(__file__), "static"))

router = APIRouter()

@router.get("/{path:path}", response_model=ContentModel)
def get_static_content(path: str) -> ContentModel:
    f = op.abspath(op.join(CONTENT_DIR, path))
    # Do not serve files outside of the content directory
    if not f.startswith(CONTENT_DIR + op.sep) or not op.isfile(f):
        raise HTTPException(status_code=404, detail="File not found")

    with open(f, "r") as file:
        content = file.read()

    return ContentModel(path=path, content=content)

