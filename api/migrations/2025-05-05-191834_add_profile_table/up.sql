CREATE TABLE IF NOT EXISTS pending_profile (
	discord_id        BIGINT      PRIMARY KEY,
	email             TEXT        NOT NULL UNIQUE,
	confirmation_code TEXT        NOT NULL UNIQUE,
	registered_at     TIMESTAMP   NOT NULL        DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS verified_profile (
	discord_id        BIGINT      PRIMARY KEY,
	email             TEXT        NOT NULL UNIQUE,
	verified_at       TIMESTAMP   NOT NULL        DEFAULT NOW()
);
