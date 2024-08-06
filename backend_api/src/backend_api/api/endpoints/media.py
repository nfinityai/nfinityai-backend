from libcloud.storage.drivers.local import LocalStorageDriver
from libcloud.storage.types import (
    ObjectDoesNotExistError,
)
from sqlalchemy_file.storage import StorageManager
from starlette.responses import (
    FileResponse,
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)

from fastapi import APIRouter, Path

router = APIRouter()


@router.get("/{storage}/{file_id}", response_class=FileResponse)
async def serve_files(storage: str = Path(...), file_id: str = Path(...)):
    try:
        file = StorageManager.get_file(f"{storage}/{file_id}")
        if isinstance(file.object.driver, LocalStorageDriver):
            """If file is stored in local storage, just return a
            FileResponse with the fill full path."""
            return FileResponse(
                file.get_cdn_url(), media_type=file.content_type, filename=file.filename  # type: ignore
            )
        elif cdn_url := file.get_cdn_url():
            """If file has public url, redirect to this url"""
            return RedirectResponse(cdn_url)
        else:
            """Otherwise, return a streaming response"""
            return StreamingResponse(
                file.object.as_stream(),
                media_type=file.content_type,
                headers={"Content-Disposition": f"attachment;filename={file.filename}"},
            )
    except ObjectDoesNotExistError:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    except RuntimeError as e:
        if "storage has not been added" in str(e):
            return JSONResponse(
                {"detail": f"Storage '{storage}' has not been configured"}, status_code=400
            )
        return JSONResponse({"detail": str(e)}, status_code=500)
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
