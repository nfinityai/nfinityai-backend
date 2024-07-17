import base64
from functools import wraps
import time


def encode_string(s: str) -> str:
    return base64.b64encode(s.encode()).decode()

def decode_string(s: str) -> str:
    return base64.b64decode(s).decode()



def measured(async_func):
    @wraps(async_func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await async_func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper
