from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from models.config import Config as GuildConfig

from web_config.discord import get_user_guilds, guild_icon_cdn_url, user_is_authorized
from web_config.templates import templates


router = APIRouter()


@router.get("/")
async def index(request: Request):
    token = request.session["token"]
    user_guilds = await get_user_guilds(token)

    stored_guild_ids = list(map(lambda c: str(c.guild_id), await GuildConfig.get_all()))

    available_guilds = list(filter(lambda g: g["id"] in stored_guild_ids, user_guilds))

    available_guilds = list(
        map(
            lambda g: {
                "id": g["id"],
                "name": g["name"],
                "icon": guild_icon_cdn_url(g["id"], g.get("icon")),
            },
            available_guilds,
        )
    )

    if len(available_guilds) == 0:
        return templates.TemplateResponse("no_guilds.html", {"request": request})
    elif len(available_guilds) == 1:
        g = available_guilds[0]
        return RedirectResponse(f"/config/{g['id']}")
    else:
        return templates.TemplateResponse(
            "select_guild.html", {"request": request, "guilds": available_guilds}
        )


@router.get("/config/{id}")
async def config(request: Request, id: str):
    token = request.session["token"]

    if not await user_is_authorized(id, token):
        return templates.TemplateResponse("forbidden.html", {"request", request})

    return templates.TemplateResponse("config_guild.html", {"request": request})
