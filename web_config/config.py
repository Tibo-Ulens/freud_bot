import os


class AppConfig:
    BASE_URL: str
    SESSION_COOKIE_DOMAIN: str
    SESSION_COOKIE_NAME: str

    DISCORD_OAUTH_CLIENT_ID: str
    DISCORD_OAUTH_CLIENT_SECRET: str

    DISCORD_BOT_TOKEN: str

    def __init__(self):
        self.BASE_URL = os.environ["BASE_URL"]
        self.SESSION_COOKIE_DOMAIN = os.environ["SESSION_COOKIE_DOMAIN"]
        self.SESSION_COOKIE_NAME = os.environ["SESSION_COOKIE_NAME"]

        with open("/run/secrets/discord_oauth_credentials") as secret:
            self.DISCORD_OAUTH_CLIENT_ID = secret.readline().rstrip("\n")
            self.DISCORD_OAUTH_CLIENT_SECRET = secret.readline().rstrip("\n")

        with open("/run/secrets/discord_token") as secret:
            self.DISCORD_BOT_TOKEN = secret.readline().rstrip("\n")


Config = AppConfig()
