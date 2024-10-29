//! Discord API routes and datatypes

use axum::async_trait;
use axum::extract::{FromRef, FromRequestParts};
use axum::response::{IntoResponse, Redirect, Response};
use axum_extra::extract::cookie::Key;
use axum_extra::extract::PrivateCookieJar;
use http::request::Parts;
use redis::AsyncCommands;
use serde::{Deserialize, Serialize};

use crate::error::{AuthorizationError, Error};
use crate::{CachePool, CookieConfig};

/// The user data that's returned from the Discord OAuth API and which is also
/// needed within this application
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DiscordUser {
	id:       String,
	username: String,
	avatar:   Option<String>,
}

#[async_trait]
impl<S> FromRequestParts<S> for DiscordUser
where
	CookieConfig: FromRef<S>,
	Key: FromRef<S>,
	CachePool: FromRef<S>,
	S: Send + Sync,
{
	type Rejection = Response;

	async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
		let cookie_cfg = CookieConfig::from_ref(state);
		let key = Key::from_ref(state);
		let cache_pool = CachePool::from_ref(state);

		let jar = PrivateCookieJar::from_headers(&parts.headers, key);

		let Some(access_token_cookie) = jar.get(&cookie_cfg.access_token_cookie_name) else {
			match jar.get(&cookie_cfg.refresh_token_cookie_name) {
				None => {
					return Err(Error::AuthorizationError(
						AuthorizationError::MissingAccessTokenCookie,
					)
					.into_response());
				},
				Some(_) => {
					return Err(Redirect::temporary("/auth/refresh").into_response());
				},
			}
		};

		let user_data: Self = {
			let mut conn =
				cache_pool.get().await.map_err(Error::from).map_err(IntoResponse::into_response)?;

			let json_str: String = conn
				.get(access_token_cookie.value())
				.await
				.map_err(Error::from)
				.map_err(IntoResponse::into_response)?;

			serde_json::from_str(&json_str)
				.map_err(Error::from)
				.map_err(IntoResponse::into_response)?
		};

		Ok(user_data)
	}
}
