CREATE TABLE IF NOT EXISTS config (
	guild_id SERIAL PRIMARY KEY,

	verified_role                BIGINT UNIQUE,
	admin_role                   BIGINT UNIQUE,
	logging_channel              BIGINT UNIQUE,
	verification_logging_channel BIGINT UNIQUE,
	confession_approval_channel  BIGINT UNIQUE,
	confession_channel           BIGINT UNIQUE,

	pin_reaction_threshold INTEGER NOT NULL DEFAULT 5,

	verify_email_message     TEXT NOT NULL DEFAULT 'Please go to https://freudbot.org/verify to verify your email',
	already_verified_message TEXT NOT NULL DEFAULT 'You are already verified',
	welcome_message          TEXT NOT NULL DEFAULT 'Welcome to {guild_name}',

	verification_email_smtp_user     TEXT,
	verification_email_smtp_password TEXT
);
