// @generated automatically by Diesel CLI.

diesel::table! {
	config (guild_id) {
		guild_id -> Text,
		verified_role -> Nullable<Text>,
		admin_role -> Nullable<Text>,
		logging_channel -> Nullable<Text>,
		verification_logging_channel -> Nullable<Text>,
		confession_approval_channel -> Nullable<Text>,
		confession_channel -> Nullable<Text>,
		pin_reaction_threshold -> Int4,
		request_verification_message -> Text,
	}
}

diesel::table! {
	pending_profile (discord_id) {
		discord_id -> Text,
		email -> Text,
		confirmation_code -> Text,
		registered_at -> Timestamp,
	}
}

diesel::table! {
	verified_profile (discord_id) {
		discord_id -> Text,
		email -> Text,
		verified_at -> Timestamp,
	}
}

diesel::allow_tables_to_appear_in_same_query!(config, pending_profile, verified_profile,);
