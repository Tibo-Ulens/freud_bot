from web_config.config import Config
from web_config.session import http_session


class AccessTokenResponse:
    def __init__(self, d: dict):
        self.access_token = d["access_token"]
        self.token_type = d["token_type"]
        self.expires_in = d["expires_in"]
        self.refresh_token = d["refresh_token"]
        self.scope = d["scope"]


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


async def get_user(access_token: str) -> DiscordUser:
    pass
