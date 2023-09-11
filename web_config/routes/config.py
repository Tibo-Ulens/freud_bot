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
    manageable_guilds = list(filter(lambda g: can_manage(g), user_guilds))

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
    elif len(available_guilds) == 1:
        g = available_guilds[0]
        return RedirectResponse(f"/config/{g['id']}")
    else:
        return templates.TemplateResponse(
            "select_guild.html", {"request": request, "guilds": available_guilds}
        )


@router.get("/config/{guild_id}")
async def show_config(request: Request, guild_id: str):
    [config, guild, channels] = await asyncio.gather(
        *[
            GuildConfig.get(int(guild_id)),
            get_guild(guild_id),
            get_guild_channels(guild_id),
        ]
    )
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

    admin_role = str(config.admin_role)
    logging_channel = str(config.logging_channel)

    verified_role = str(config.verified_role)
    verification_channel = str(config.verification_channel)

    confession_approval_channel = str(config.confession_approval_channel)
    confession_channel = str(config.confession_channel)

    import sys

    print(
        f"guild: {guild}\nroles: {roles}\nchannels: {channels}\nadminrole: {admin_role}",
        file=sys.stderr,
    )

    return templates.TemplateResponse(
        "config_guild.html",
        {
            "request": request,
            "guild": guild,
            "roles": roles,
            "channels": channels,
            "admin_role": admin_role,
            "logging_channel": logging_channel,
            "verified_role": verified_role,
            "verification_channel": verification_channel,
            "confession_approval_channel": confession_approval_channel,
            "confession_channel": confession_channel,
            "pin_reaction_threshold": config.pin_reaction_threshold,
        },
    )


@router.post("/config/{guild_id}")
async def update_config(request: Request, guild_id: str):
    import sys

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
