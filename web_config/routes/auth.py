from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from web_config.config import Config
from web_config.discord import get_access_token


router = APIRouter()


@router.get("/login")
async def login():
    authorize_url = "https://discord.com/api/oauth2/authorize"

    params = {
        "client_id": Config.discord_oauth_client_id,
        "response_type": "code",
        "scope": "identify%20guilds",
        "redirect_uri": f"{Config.base_url}/callback",
    }

    authorize_url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return RedirectResponse(authorize_url, status_code=302)


@router.get("/callback")
async def callback(request: Request, code: str):
    token_response = await get_access_token(code)
    token = token_response.access_token

    request.session["token"] = token

    return RedirectResponse("/", status_code=302)
