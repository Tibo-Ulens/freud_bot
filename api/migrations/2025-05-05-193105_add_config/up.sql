CREATE TABLE IF NOT EXISTS config (
	guild_id TEXT PRIMARY KEY,

	verified_role                TEXT UNIQUE,
	admin_role                   TEXT UNIQUE,
	logging_channel              TEXT UNIQUE,
	verification_logging_channel TEXT UNIQUE,
	confession_approval_channel  TEXT UNIQUE,
	confession_channel           TEXT UNIQUE,

	pin_reaction_threshold INTEGER NOT NULL DEFAULT 5,

	request_verification_message TEXT NOT NULL DEFAULT 'Please go to https://freudbot.org/verify to verify your email'
);
