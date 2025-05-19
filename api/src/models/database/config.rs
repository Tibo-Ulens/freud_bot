use diesel::prelude::*;
use diesel_async::RunQueryDsl;
use serde::{Deserialize, Serialize};

use super::PgU64;
use crate::DbConn;
use crate::schema::config;

#[derive(Clone, Debug, Deserialize, Identifiable, Insertable, Queryable, Selectable, Serialize)]
#[diesel(table_name = config)]
#[diesel(primary_key(guild_id))]
pub struct Config {
	pub guild_id:                     PgU64,
	pub verified_role:                Option<PgU64>,
	pub admin_role:                   Option<PgU64>,
	pub logging_channel:              Option<PgU64>,
	pub verification_logging_channel: Option<PgU64>,
	pub confession_approval_channel:  Option<PgU64>,
	pub confession_channel:           Option<PgU64>,
	pub pin_reaction_threshold:       i32,
	pub request_verification_message: String,
}

impl Config {
	/// Get a list of all [`Config`]s
	pub async fn all(conn: &mut DbConn) -> QueryResult<Vec<Self>> {
		use crate::schema::config::dsl::*;

		config.load(conn).await
	}
}
