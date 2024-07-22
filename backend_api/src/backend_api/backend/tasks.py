from functools import lru_cache
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore


# Initialize a SQLAlchemyJobStore with SQLite database
jobstores = {
    'default': MemoryJobStore()
}

@lru_cache
def get_scheduler():
    return AsyncIOScheduler(jobstores=jobstores)


scheduler = get_scheduler()