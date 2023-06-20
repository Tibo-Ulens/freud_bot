import logging
import random
import string

from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

from web_config.config import Config


logger = logging.getLogger("webconfig")


app = FastAPI()

session_key = "".join([random.choice(string.printable) for _ in range(64)])
app.add_middleware(
    SessionMiddleware,
    secret_key="",
    session_cookie=Config.SESSION_COOKIE_NAME,
    max_age=None,
    same_site="lax",
    https_only=True,
)


@app.middleware("http")
async def check_authorized(request: Request, call_next):
    logger.info(request.base_url.path)

    return await call_next(request)


@app.get("/")
async def index():
    return "hello"
