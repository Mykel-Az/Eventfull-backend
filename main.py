from fastapi import FastAPI, Request, Response, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter


from routes.user_auth import auth as Authentication
from routes.Events import vent as Eventing
from routes.Ticketing import vent as Ticketing
from routes.Analytics import lytics as Analytics


# logger_system = logging.getLogger(__name__)

# REDIS_URL = "redis-1523.c291.ap-northeast-1-2.ec2.cloud.redislabs.com"
# REDIS_PASSWORD = "1234"
# REDIS_PORT = 1492


app = FastAPI(title="FastAPI Event Backend")


app.include_router(Authentication, prefix="/auth", tags=["Authentication"])
app.include_router(Eventing, prefix="/event", tags=["Eventing"])
app.include_router(Ticketing, prefix="/ticket", tags=["Ticketing"])
app.include_router(Analytics, prefix="/stats", tags=["Analytics"])



@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def loader():
    return {"message": "Server up and running"}



@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    redis_connection = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await FastAPILimiter.init(redis_connection)


# @app.on_event("startup")
# def startup():
#   redis_cache = Cyrus(
#     logger_system = logger_system ,
#     host_url = REDIS_URL ,
#     port = REDIS_PORT ,
#     password = REDIS_PASSWORD ,
#     prefix = "myapi-cache" ,
#     response_header = "X-MyAPI-Cache" ,
#     ignore_arg_types = [Request , Response , Session]
#   )


















































































































































































































































































@app.get("/timer")
def timer():
    pass