import os


class AppConfig:
    base_url: str
    session_cookie_domain: str
    session_cookie_name: str

    discord_oauth_client_id: str
    discord_oauth_client_secret: str

    discord_bot_token: str

    def __init__(self):
        self.base_url = os.environ["BASE_URL"]
        self.session_cookie_domain = os.environ["SESSION_COOKIE_DOMAIN"]
        self.session_cookie_name = os.environ["SESSION_COOKIE_NAME"]

        with open("/run/secrets/discord_oauth_credentials", encoding="UTF-8") as secret:
            self.discord_oauth_client_id = secret.readline().rstrip("\n")
            self.discord_oauth_client_secret = secret.readline().rstrip("\n")

        with open("/run/secrets/discord_token", encoding="UTF-8") as secret:
            self.discord_bot_token = secret.readline().rstrip("\n")


Config = AppConfig()
