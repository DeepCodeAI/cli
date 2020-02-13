from functools import wraps
import time
import logging
import inspect
import asyncio

logger = logging.getLogger('deepcode')


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f(*args, **kwargs))
        #return asyncio.run() # supported only from 3.7+

    return wrapper

def profile_speed(func):
    
    log_timing = lambda d: logger.debug("- {:6.2f} sec: Done - \"{}\"".format(
                    d, func.__doc__ or func.__name__))

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                log_timing(time.time() - start_time)
        
        return wrapper
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                log_timing(time.time() - start_time)
        
        return wrapper
