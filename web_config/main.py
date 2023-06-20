import random
import string
import logging
import logging.config
from os import path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from web_config.config import Config
from web_config.routes.auth import router as auth_router
from web_config.routes.config import router as config_router
from web_config.session import http_session

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def check_authorized(request: Request, call_next):
    path = request.url.path
    if path == "/login" or path == "/callback":
        return await call_next(request)

    token = request.session.get("token")
    if token is None:
        return RedirectResponse("/login")

    auth_header = {"Authorization": f"Bearer {token}"}

    async with http_session.get(
        "https://discord.com/api/oauth2/@me", headers=auth_header
    ) as res:
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
app.include_router(config_router)
