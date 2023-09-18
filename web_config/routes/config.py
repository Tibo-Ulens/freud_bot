import asyncio

from fastapi import APIRouter, Request, status
from fastapi.datastructures import FormData
from fastapi.responses import RedirectResponse

from models.config import Config as GuildConfig

from web_config.discord import (
    can_manage,
    get_user_guilds,
    guild_icon_cdn_url,
    get_guild,
    get_guild_channels,
)
from web_config.templates import templates


router = APIRouter()


@router.get("/")
async def index(request: Request):
    token = request.session["token"]

    user_guilds = await get_user_guilds(token)
    manageable_guilds = list(filter(can_manage, user_guilds))

    stored_guild_ids = list(map(lambda c: str(c.guild_id), await GuildConfig.get_all()))

    available_guilds = list(
        map(
            lambda g: {
                "id": g["id"],
                "name": g["name"],
                "icon": guild_icon_cdn_url(g["id"], g.get("icon")),
            },
            filter(lambda g: g["id"] in stored_guild_ids, manageable_guilds),
        )
    )

    if len(available_guilds) == 0:
        return templates.TemplateResponse("no_guilds.html", {"request": request})

    if len(available_guilds) == 1:
        guild = available_guilds[0]
        return RedirectResponse(f"/config/{guild['id']}")

    return templates.TemplateResponse(
        "select_guild.html", {"request": request, "guilds": available_guilds}
    )


@router.get("/config/{guild_id}")
async def show_config(request: Request, guild_id: str):
    typed_list: tuple[GuildConfig, dict, list[dict]] = await asyncio.gather(
        *[
            GuildConfig.get(int(guild_id)),
            get_guild(guild_id),
            get_guild_channels(guild_id),
        ]
    )
    [config, guild, channels] = typed_list

    roles = guild["roles"]

    guild = {
        "id": guild["id"],
        "name": guild["name"],
        "icon": guild_icon_cdn_url(guild["id"], guild.get("icon")),
    }

    roles = list(map(lambda r: {"id": r["id"], "name": r["name"]}, roles))

    channels = list(
        map(
            lambda c: {"id": c["id"], "name": c["name"]},
            filter(lambda c: c["type"] == 0, channels),
        )
    )

    return templates.TemplateResponse(
        "config_guild.html",
        {
            "request": request,
            "guild": guild,
            "roles": roles,
            "channels": channels,
            "admin_role": str(config.admin_role),
            "logging_channel": str(config.logging_channel),
            "verified_role": str(config.verified_role),
            "confession_approval_channel": str(config.confession_approval_channel),
            "confession_channel": str(config.confession_channel),
            "pin_reaction_threshold": int(config.pin_reaction_threshold),
            "verify_email_message": str(config.verify_email_message),
            "new_email_message": str(config.new_email_message),
            "invalid_email_message": str(config.invalid_email_message),
            "duplicate_email_message": str(config.duplicate_email_message),
            "verify_code_message": str(config.verify_code_message),
            "invalid_code_message": str(config.invalid_code_message),
            "already_verified_message": str(config.already_verified_message),
            "welcome_message": str(config.welcome_message),
        },
    )


@router.post("/config/{guild_id}")
async def update_config(request: Request, guild_id: str):
    typed_list: tuple[GuildConfig, FormData] = await asyncio.gather(
        *[
            GuildConfig.get(int(guild_id)),
            request.form(),
        ]
    )

    [config, form] = typed_list

    config = config.update(form._dict)

    await config.save()

    return RedirectResponse(
        f"/config/{guild_id}", status_code=status.HTTP_303_SEE_OTHER
    )
