use diesel::prelude::*;
use diesel_async::RunQueryDsl;
use serde::{Deserialize, Serialize};

use crate::DbConn;
use crate::routes::PatchConfigData;
use crate::schema::config;

#[derive(Clone, Debug, Deserialize, Identifiable, Insertable, Queryable, Selectable, Serialize)]
#[diesel(table_name = config)]
#[diesel(primary_key(guild_id))]
pub struct Config {
	pub guild_id:                     String,
	pub verified_role:                Option<String>,
	pub admin_role:                   Option<String>,
	pub logging_channel:              Option<String>,
	pub verification_logging_channel: Option<String>,
	pub confession_approval_channel:  Option<String>,
	pub confession_channel:           Option<String>,
	pub pin_reaction_threshold:       i32,
	pub request_verification_message: String,
}

impl Config {
	/// Get a list of all [`Config`]s
	pub async fn all(conn: &mut DbConn) -> QueryResult<Vec<Self>> {
		use crate::schema::config::dsl::*;

		config.load(conn).await
	}

	/// Apply a [`Patch`](PatchConfigData) to a row
	pub async fn patch(
		query_id: String,
		patch: PatchConfigData,
		conn: &mut DbConn,
	) -> QueryResult<Self> {
		use crate::schema::config::dsl::*;

		diesel::update(config.find(query_id)).set(patch).get_result(conn).await
	}
}
