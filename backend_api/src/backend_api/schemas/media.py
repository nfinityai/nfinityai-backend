

from pydantic import BaseModel


class Thumbnail(BaseModel):
    path: str
    url: str | None = None


class FileInfo(BaseModel):
    filename: str
    content_type: str
    path: str
    upload_storage: str
    file_id: str
