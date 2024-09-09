# import random
# import string
import logging
import logging.config
from os import path

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
# from starlette.middleware.sessions import SessionMiddleware

from api.config import Config
from api.routes.auth import router as auth_router
from api.routes.user import router as user_router
from api.session import http_session

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)


app = FastAPI()


@app.middleware("http")
async def check_authorized(request: Request, call_next):
    req_path = request.url.path
    if req_path.startswith("/auth"):
        return await call_next(request)

    access_token = request.cookies.get("DISCORD_ACCESS_TOKEN")
    refresh_token = request.cookies.get("DISCORD_REFRESH_TOKEN")

    if not refresh_token:
        return Response(status_code=401)

    if refresh_token and not access_token:
        async with http_session.get(f"{Config.base_url}/auth/refresh?refresh_token={refresh_token}") as res:
            refresh_data = await res.json()
            access_token = refresh_data.discord_access_token

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        "https://discord.com/api/oauth2/@me", headers=auth_header
    ) as res:
        if res.status == 401:
            return RedirectResponse("/login")

        user_data = await res.json()
        request.state.user_data = user_data["user"]

        return await call_next(request)


app.add_middleware(GZipMiddleware)


app.include_router(auth_router, prefix="/auth")
app.include_router(user_router)