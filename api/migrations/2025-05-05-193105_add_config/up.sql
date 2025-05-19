CREATE TABLE IF NOT EXISTS config (
	guild_id BIGINT PRIMARY KEY,

	verified_role                BIGINT UNIQUE,
	admin_role                   BIGINT UNIQUE,
	logging_channel              BIGINT UNIQUE,
	verification_logging_channel BIGINT UNIQUE,
	confession_approval_channel  BIGINT UNIQUE,
	confession_channel           BIGINT UNIQUE,

	pin_reaction_threshold INTEGER NOT NULL DEFAULT 5,

	request_verification_message TEXT NOT NULL DEFAULT 'Please go to https://freudbot.org/verify to verify your email'
);
