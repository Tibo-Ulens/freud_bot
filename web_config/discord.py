from models.config import Config as GuildConfig

from web_config.config import Config
from web_config.session import http_session


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


async def get_access_token(auth_code: str) -> AccessTokenResponse:
    """Exchange an authorization code for an access token"""

    token_form = {
        "client_id": Config.DISCORD_OAUTH_CLIENT_ID,
        "client_secret": Config.DISCORD_OAUTH_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": f"{Config.BASE_URL}/callback",
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


async def get_user_guilds(access_token: str) -> list[any]:
    """Get the every guild the user is in"""

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        "https://discord.com/api/users/@me/guilds", headers=auth_header
    ) as res:
        data = await res.json()
        return data


async def user_is_authorized(guild_id: str, access_token: str) -> bool:
    """
    Check if the current user meets the authorization requirements to
    configure the guild
    """

    guild_config = await GuildConfig.get(int(guild_id))
    if guild_config is None:
        return False

    guild_admin_role = str(guild_config.admin_role)

    auth_header = {"Authorization": f"Bearer {access_token}"}

    async with http_session.get(
        f"https://discord.com/api//users/@me/guilds/{guild_id}/member",
        headers=auth_header,
    ) as res:
        member_obj = await res.json()
        roles = member_obj["roles"]

        perms = member_obj.get("permissions")
        if perms is None:
            return guild_admin_role in roles

        manage_guild_flag = (perms >> 3) & 0x1

        return manage_guild_flag == 1 or guild_admin_role in roles
