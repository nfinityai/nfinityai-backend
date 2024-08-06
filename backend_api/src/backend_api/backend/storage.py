import contextlib
from libcloud.storage.providers import get_driver
from libcloud.storage.types import (
    ContainerAlreadyExistsError,
    Provider,
)
from sqlalchemy_file.storage import StorageManager
from backend_api.backend.config import get_settings
import os



def init_storage():
    upload_dir = get_settings().media_upload_dir
    # Create the upload directory if it doesn't already
    os.makedirs(upload_dir, 0o777, exist_ok=True)
    driver = get_driver(Provider.LOCAL)(upload_dir)

    with contextlib.suppress(ContainerAlreadyExistsError):
        driver.create_container(container_name="category_icons")
    container = driver.get_container(container_name="category_icons")
    StorageManager.add_storage("category_icons", container)
