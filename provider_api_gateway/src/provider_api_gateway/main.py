import os

import uvicorn
from fastapi import FastAPI

from provider_api_gateway.api.router import api_router
from provider_api_gateway.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(title="Provider API Gateway", version="0.0.1")

# Include the API routers
app.include_router(api_router)


if __name__ == "__main__":
    logger.info("Starting provider API gateway")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
