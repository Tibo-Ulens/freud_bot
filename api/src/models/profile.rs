use base64::Engine;
use base64::prelude::BASE64_URL_SAFE;
use chrono::NaiveDateTime;
use diesel::prelude::*;
use diesel_async::scoped_futures::ScopedFutureExt;
use diesel_async::{AsyncConnection, RunQueryDsl};
use lettre::message::Mailbox;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::DbConn;
use crate::error::Error;
use crate::schema::{pending_profile, verified_profile};

#[derive(
	Clone, Debug, Deserialize, Hash, Identifiable, Insertable, Queryable, Selectable, Serialize,
)]
#[diesel(table_name = pending_profile)]
#[diesel(primary_key(discord_id))]
pub struct PendingProfile {
	pub discord_id:        String,
	pub email:             String,
	pub confirmation_code: String,
	pub registered_at:     NaiveDateTime,
}

#[derive(Clone, Debug, Deserialize, Identifiable, Insertable, Queryable, Selectable, Serialize)]
#[diesel(table_name = verified_profile)]
#[diesel(primary_key(discord_id))]
pub struct VerifiedProfile {
	pub discord_id:  String,
	pub email:       String,
	pub verified_at: NaiveDateTime,
}

#[derive(AsChangeset, Clone, Debug, Deserialize, Insertable, Serialize)]
#[diesel(table_name = pending_profile)]
#[diesel(primary_key(discord_id))]
struct NewPendingProfile {
	discord_id:        String,
	email:             String,
	confirmation_code: String,
}

#[derive(Clone, Debug, Deserialize, Insertable, Serialize)]
#[diesel(table_name = verified_profile)]
#[diesel(primary_key(discord_id))]
struct NewVerifiedProfile {
	discord_id: String,
	email:      String,
}

impl TryFrom<&PendingProfile> for Mailbox {
	type Error = Error;

	fn try_from(value: &PendingProfile) -> Result<Mailbox, Error> {
		Ok(Mailbox::new(None, value.email.parse()?))
	}
}

impl From<PendingProfile> for NewVerifiedProfile {
	fn from(value: PendingProfile) -> Self {
		Self { discord_id: value.discord_id, email: value.email }
	}
}

impl PendingProfile {
	/// Create and store a new [`PendingProfile`] for a given discord user or
	/// simply update the email if there is already a profile stored
	#[instrument(skip_all)]
	pub async fn new_or_update(
		discord_id: String,
		email: String,
		conn: &mut DbConn,
	) -> QueryResult<Self> {
		let confirmation_code = BASE64_URL_SAFE.encode(Uuid::new_v4().as_bytes());

		let new_profile = NewPendingProfile { discord_id, email, confirmation_code };

		diesel::insert_into(pending_profile::dsl::pending_profile)
			.values(&new_profile)
			.on_conflict(pending_profile::dsl::discord_id)
			.do_update()
			.set(&new_profile)
			.returning(PendingProfile::as_returning())
			.get_result(conn)
			.await
	}

	/// Find a [`PendingProfile`] by its discord ID
	pub async fn find(query_id: String, conn: &mut DbConn) -> QueryResult<Self> {
		use crate::schema::pending_profile::dsl::*;

		pending_profile.find(query_id).get_result(conn).await
	}

	/// Verify this [`PendingProfile`] and turn it into a [`VerifiedProfile`]
	///
	/// The profile will be removed from the `pending_profile` table and added
	/// to the `verified_profile` table
	#[instrument(skip_all)]
	pub async fn verify(self, conn: &mut DbConn) -> QueryResult<VerifiedProfile> {
		let new_verified_profile: NewVerifiedProfile = self.clone().into();

		let res = conn
			.transaction(|conn| {
				async move {
					diesel::delete(&self).execute(conn).await?;

					diesel::insert_into(verified_profile::dsl::verified_profile)
						.values(new_verified_profile)
						.returning(VerifiedProfile::as_returning())
						.get_result(conn)
						.await
				}
				.scope_boxed()
			})
			.await?;

		info!("verified profile {} - {}", res.discord_id, res.email);

		Ok(res)
	}
}
