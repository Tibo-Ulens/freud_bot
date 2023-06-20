import logging
import random
import string

import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from web_config.config import Config
from web_config.routes.auth import router as auth_router


logger = logging.getLogger("webconfig")


app = FastAPI()


@app.middleware("http")
async def check_authorized(request: Request, call_next):
    path = request.url.path
    if path == "/login" or path == "/callback":
        return await call_next(request)

    token = request.session.get("token")
    if token is None:
        return RedirectResponse("/login")

    auth_header = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/oauth2/@me", headers=auth_header
        ) as res:
            logger.info(res.status)

            if res.status == 401:
                return RedirectResponse("/login")

            return await call_next(request)


session_key = "".join([random.choice(string.printable) for _ in range(64)])
app.add_middleware(
    SessionMiddleware,
    secret_key="",
    session_cookie=Config.SESSION_COOKIE_NAME,
    max_age=None,
    same_site="lax",
    https_only=True,
)
app.add_middleware(GZipMiddleware)


app.include_router(auth_router)


@app.get("/")
async def index():
    return "hello"
