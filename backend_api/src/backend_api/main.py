import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api.api.router import api_router
from backend_api.backend.logging import configure_logging, get_logger
from backend_api.backend.tasks import scheduler
from backend_api import tasks  # noqa: F401

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Backend API", version="0.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the API routers
app.include_router(api_router)


if __name__ == "__main__":
    logger.info("Starting backend API")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
