use axum::Json;
use axum::extract::{Path, State};
use axum::response::{IntoResponse, NoContent, Response};
use serde::{Deserialize, Serialize};

use super::DiscordUser;
use crate::DbPool;
use crate::error::Error;
use crate::mailer::Mailer;
use crate::models::profile::{PendingProfile, VerifiedProfile};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct VerifyData {
	email: String,
}

#[instrument(skip(pool, mailer, base_url))]
pub async fn request_verify(
	State(pool): State<DbPool>,
	State(mailer): State<Mailer>,
	State(base_url): State<String>,
	user: DiscordUser,
	Json(data): Json<VerifyData>,
) -> Result<impl IntoResponse, Error> {
	let mut conn = pool.get().await?;

	if VerifiedProfile::exists(user.id.clone(), &mut conn).await? {
		return Err(Error::Duplicate("discord_id".to_string()));
	}

	if VerifiedProfile::exists_email(data.email.clone(), &mut conn).await? {
		return Err(Error::Duplicate("email".to_string()));
	}

	let pending_profile = PendingProfile::new_or_update(user.id, data.email, &mut conn).await?;

	mailer
		.send_verification_link(&pending_profile, &pending_profile.confirmation_code, &base_url)
		.await?;

	Ok(NoContent)
}

#[instrument(skip(pool))]
pub async fn confirm_verify(
	State(pool): State<DbPool>,
	Path(confirmation_code): Path<String>,
	user: DiscordUser,
) -> Result<Response, Error> {
	let mut conn = pool.get().await?;

	let pending_profile = PendingProfile::find(user.id, &mut conn).await?;

	if confirmation_code != pending_profile.confirmation_code {
		return Err(Error::InvalidConfirmationCode);
	}

	pending_profile.verify(&mut conn).await?;

	Ok(NoContent.into_response())
}

#[instrument(skip_all)]
pub async fn is_verified(State(pool): State<DbPool>, user: DiscordUser) -> Result<Response, Error> {
	let mut conn = pool.get().await?;

	if VerifiedProfile::exists(user.id, &mut conn).await? {
		return Ok(Json(true).into_response());
	}

	Ok(Json(false).into_response())
}
