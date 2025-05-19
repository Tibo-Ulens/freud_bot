// @generated automatically by Diesel CLI.

diesel::table! {
	config (guild_id) {
		guild_id -> Int8,
		verified_role -> Nullable<Int8>,
		admin_role -> Nullable<Int8>,
		logging_channel -> Nullable<Int8>,
		verification_logging_channel -> Nullable<Int8>,
		confession_approval_channel -> Nullable<Int8>,
		confession_channel -> Nullable<Int8>,
		pin_reaction_threshold -> Int4,
		request_verification_message -> Text,
	}
}

diesel::table! {
	pending_profile (discord_id) {
		discord_id -> Int8,
		email -> Text,
		confirmation_code -> Text,
		registered_at -> Timestamp,
	}
}

diesel::table! {
	verified_profile (discord_id) {
		discord_id -> Int8,
		email -> Text,
		verified_at -> Timestamp,
	}
}

diesel::allow_tables_to_appear_in_same_query!(config, pending_profile, verified_profile,);
