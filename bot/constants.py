DISCORD_TOKEN: str
with open("/run/secrets/discord_token") as secret:
    DISCORD_TOKEN = secret.readline().rstrip("\n")

GMAIL_APP_PASSWORD: str
with open("/run/secrets/gmail_app_password") as secret:
    GMAIL_APP_PASSWORD = secret.readline().rstrip("\n")

VERIFIED_ROLE = "Verified"

VERIFY_CHANNEL = "1008833438041780224"
