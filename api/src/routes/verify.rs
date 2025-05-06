use std::hash::{DefaultHasher, Hash, Hasher};

use axum::Json;
use axum::extract::State;
use axum::response::IntoResponse;
use base64::Engine;
use base64::prelude::BASE64_STANDARD;
use serde::{Deserialize, Serialize};

use super::DiscordUser;
use crate::DbPool;
use crate::error::Error;
use crate::models::profile::PendingProfile;

#[derive(Clone, Debug, Deserialize, Serialize)]
struct VerifyData {
	email: String,
}

#[instrument(skip(pool))]
pub async fn request_verify(
	State(pool): State<DbPool>,
	Json(data): Json<VerifyData>,
	user: DiscordUser,
) -> Result<impl IntoResponse, Error> {
	let mut conn = pool.get().await?;

	let pending_profile =
		PendingProfile::new(user.id, data.email, &mut conn).await?;

	let mut hasher = DefaultHasher::new();
	pending_profile.hash(&mut hasher);
	let confirmation_hash = hasher.finish();
	let confirmation_code =
		BASE64_STANDARD.encode(confirmation_hash.to_le_bytes());

	todo!("send an email with the confirmation code");

	Ok(())
}
