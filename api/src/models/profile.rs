use chrono::NaiveDateTime;
use diesel::prelude::*;
use diesel_async::RunQueryDsl;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::DbConn;
use crate::schema::{pending_profile, verified_profile};

#[derive(
	Clone,
	Debug,
	Deserialize,
	Hash,
	Identifiable,
	Insertable,
	Queryable,
	Selectable,
	Serialize,
)]
#[diesel(table_name = pending_profile)]
#[diesel(primary_key(discord_id))]
pub struct PendingProfile {
	discord_id:        String,
	email:             String,
	confirmation_code: Uuid,
	registered_at:     NaiveDateTime,
}

#[derive(
	Clone,
	Debug,
	Deserialize,
	Identifiable,
	Insertable,
	Queryable,
	Selectable,
	Serialize,
)]
#[diesel(table_name = verified_profile)]
#[diesel(primary_key(discord_id))]
pub struct VerifiedProfile {
	discord_id:  String,
	email:       String,
	verified_at: NaiveDateTime,
}

#[derive(Clone, Debug, Deserialize, Insertable, Serialize)]
#[diesel(table_name = pending_profile)]
#[diesel(primary_key(discord_id))]
struct NewProfile {
	discord_id:        String,
	email:             String,
	confirmation_code: Uuid,
}

impl PendingProfile {
	pub async fn new(
		discord_id: String,
		email: String,
		conn: &mut DbConn,
	) -> QueryResult<Self> {
		let confirmation_code = Uuid::new_v4();
		let new_profile = NewProfile { discord_id, email, confirmation_code };

		diesel::insert_into(pending_profile::dsl::pending_profile)
			.values(new_profile)
			.returning(PendingProfile::as_returning())
			.get_result(conn)
			.await
	}
}
