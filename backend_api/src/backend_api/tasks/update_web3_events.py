from datetime import datetime
from backend_api.backend.session import get_session
from backend_api.backend.config import get_settings
from backend_api.services.web3 import Web3EventService
from backend_api.backend.tasks import scheduler


@scheduler.scheduled_job("interval", minutes=1, next_run_time=datetime.now())
async def update_web3_events():
    async for session in get_session():
        async with Web3EventService(session, get_settings()) as web3_service:
            await web3_service.add_events()
