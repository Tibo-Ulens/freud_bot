from web_config.config import Config
from web_config.session import http_session


ADMINISTRATOR_FLAG = 0b1000
MANAGE_GUILD_FLAG = 0b10_0000


class AccessTokenResponse:
    def __init__(self, d: dict):
        self.access_token = d["access_token"]
        self.token_type = d["token_type"]
        self.expires_in = d["expires_in"]
        self.refresh_token = d["refresh_token"]
        self.scope = d["scope"]

    def __repr__(self) -> str:
        return f"{vars(self)}"


class DiscordUser:
    def __init__(self, d: dict):
        self.id = d["id"]
        self.username = d["username"]
        self.discriminator = d["discriminator"]

        self.global_name = d.get("global_name")
        self.avatar = d.get("avatar")
        self.bot = d.get("bot")
        self.system = d.get("system")
        self.mfa_enabled = d.get("mfa_enabled")
        self.banner = d.get("banner")
        self.accent_color = d.get("accent_color")
        self.locale = d.get("locale")
        self.verified = d.get("verified")
        self.email = d.get("email")
        self.flags = d.get("flags")
        self.premium_type = d.get("premium_type")
        self.public_flags = d.get("public_flags")

    def __repr__(self) -> str:
        return f"{vars(self)}"


def can_manage(guild: dict) -> bool:
    """Check if the ADMINISTRATOR and/or MANAGE_GUILD flags are set"""

    perms = guild["permissions"]

    return (perms & ADMINISTRATOR_FLAG) != 0 or (perms & MANAGE_GUILD_FLAG) != 0


async def get_access_token(auth_code: str) -> AccessTokenResponse:
    """Exchange an authorization code for an access token"""

    token_form = {
        "client_id": Config.discord_oauth_client_id,
        "client_secret": Config.discord_oauth_client_secret,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": f"{Config.base_url}/callback",
    }

    async with http_session.post(
        "https://discord.com/api/oauth2/token", data=token_form
    ) as res:
        data = await res.json()
        return AccessTokenResponse(data)


def guild_icon_cdn_url(guild_id: str, icon_id: str | None) -> str | None:
    """Get the discord CDN url for a guild icon"""

    if icon_id is None:
        return None

    return f"https://cdn.discordapp.com/icons/{guild_id}/{icon_id}.webp"


async def get_user(access_token: str) -> DiscordUser:
    """Get the currently logged in user"""

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        "https://discord.com/api/users/@me", headers=auth_header
    ) as res:
        data = await res.json()
        return DiscordUser(data)


async def get_user_guilds(access_token: str) -> list[dict]:
    """Get the every guild the user is in"""

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        "https://discord.com/api/users/@me/guilds", headers=auth_header
    ) as res:
        data = await res.json()
        return data


async def get_user_guild(access_token: str, guild_id) -> list[dict]:
    """Get a guild the user is in by id"""

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        "https://discord.com/api/users/@me/guilds", headers=auth_header
    ) as res:
        data: list[data] = await res.json()
        return next(filter(lambda g: g["id"] == guild_id, data), None)


async def get_guild(guild_id: str) -> dict:
    """Get a guild by ID"""

    auth_header = {"Authorization": f"Bot {Config.discord_bot_token}"}

    async with http_session.get(
        f"https://discord.com/api/guilds/{guild_id}", headers=auth_header
    ) as res:
        data = await res.json()
        return data


async def get_guild_channels(guild_id: str) -> list[dict]:
    """Get a guilds channels given its ID"""

    auth_header = {"Authorization": f"Bot {Config.discord_bot_token}"}

    async with http_session.get(
        f"https://discord.com/api/guilds/{guild_id}/channels", headers=auth_header
    ) as res:
        data = await res.json()
        return data
