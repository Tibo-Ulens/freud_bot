import aiohttp
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from web_config.models.discord import AccessTokenResponse
from web_config.config import Config


router = APIRouter()


@router.get("/login")
async def login():
    authorize_url = "https://discord.com/api/oauth2/authorize"

    params = {
        "client_id": Config.DISCORD_OAUTH_CLIENT_ID,
        "response_type": "code",
        "scope": "identify guilds guilds.members.read",
        "redirect_uri": f"{Config.BASE_URL}/callback",
    }

    authorize_url += "&" + "".join([f"{k}={v}" for k, v in params.items()])

    return RedirectResponse(authorize_url)


@router.get("/callback")
async def callback():
    pass


async def get_access_token(auth_code: str) -> AccessTokenResponse:
    token_form = {
        "client_id": Config.DISCORD_OAUTH_CLIENT_ID,
        "client_secret": Config.DISCORD_OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": f"{Config.BASE_URL}/callback",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://discord.com/api/oauth2/token", data=token_form
        ) as res:
            data = await res.json()
            return AccessTokenResponse(data)
