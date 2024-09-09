from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from api.config import Config
from api.session import http_session


router = APIRouter()


@router.get("/login")
async def login():
    authorize_url = "https://discord.com/api/oauth2/authorize"

    params = {
        "client_id": Config.discord_oauth_client_id,
        "response_type": "code",
        "scope": "identify%20guilds",
        "redirect_uri": f"{Config.base_url}/auth/callback",
    }

    authorize_url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return RedirectResponse(authorize_url, status_code=302)


@router.get("/callback")
async def callback(code: str):
    token_form = {
        "client_id": Config.discord_oauth_client_id,
        "client_secret": Config.discord_oauth_client_secret,
        "grant_type": "authorization_code",
        "redirect_uri": f"{Config.base_url}/auth/callback",
        "code": code,
        "scope": "identify guilds",
    }

    async with http_session.post(
        "https://discord.com/api/oauth2/token", data=token_form
    ) as res:
        data = await res.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        response = RedirectResponse(Config.homepage_url, status_code=302)

        response.set_cookie(
            key=Config.access_cookie_name,
            value=access_token,
            expires=datetime.now(timezone.utc) + timedelta(milliseconds=data["expires_in"]),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )

        response.set_cookie(
            key=Config.refresh_cookie_name,
            value=refresh_token,
            expires=datetime.now(timezone.utc) + timedelta(milliseconds=30 * 24 * 60 * 60 * 1000),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )

        return response

@router.get("/refresh")
async def refresh(refresh_token: str):
    token_form = {
        "client_id": Config.discord_oauth_client_id,
        "client_secret": Config.discord_oauth_client_secret,
        "grant_type": "refresh_token",
        "redirect_uri": f"{Config.base_url}/auth/callback",
        "refresh_token": refresh_token,
        "scope": "identify guilds",
    }

    async with http_session.post(
        "https://discord.com/api/oauth2/token", data=token_form
    ) as res:
        data = await res.json()

        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        response = RedirectResponse(Config.homepage_url, status_code=302)

        response.set_cookie(
            key=Config.access_cookie_name,
            value=access_token,
            expires=datetime.now(timezone.utc) + timedelta(milliseconds=data["expires_in"]),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )

        response.set_cookie(
            key=Config.refresh_cookie_name,
            value=refresh_token,
            expires=datetime.now(timezone.utc) + timedelta(milliseconds=30 * 24 * 60 * 60 * 1000),
            path="/",
            secure=False,
            httponly=True,
            samesite="lax",
        )

        return response

@router.get("/logout")
async def logout():
        response = RedirectResponse("/", status_code=302)

        response.delete_cookie(Config.access_cookie_name, path="/")
        response.delete_cookie(Config.refresh_cookie_name, path="/")
