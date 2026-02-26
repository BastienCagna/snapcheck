from pydantic import BaseModel


class ContentModel(BaseModel):
    path: str
    content: str

