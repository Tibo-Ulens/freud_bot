class AccessTokenResponse:
    def __init__(self, dict):
        self.access_token = dict["access_token"]
        self.token_type = dict["token_type"]
        self.expires_in = dict["expires_in"]
        self.refresh_token = dict["refresh_token"]
        self.scope = dict["scope"]
