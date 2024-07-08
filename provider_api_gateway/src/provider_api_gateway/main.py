from fastapi import FastAPI
import uvicorn
import os
from provider_api_gateway.api.router import api_router

app = FastAPI(title="Provider API Gateway", version="0.0.1")

# Include the API routers
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', 8000)))
