//! Discord API routes and datatypes

use axum::extract::{FromRef, FromRequestParts};
use axum::response::{IntoResponse, Response};
use deadpool_redis::redis::AsyncCommands;
use http::request::Parts;
use oauth2::AccessToken;
use serde::{Deserialize, Serialize};
use serenity::all::{Http, LightMethod, Request, Route, User};
use time::Duration;

use crate::error::{AuthorizationError, Error};
use crate::{CacheConn, CachePool, CookieConfig};

/// The user data that's returned from the Discord OAuth API and which is also
/// needed within this application
#[derive(Clone, Debug, Deserialize, Serialize)]
#[repr(transparent)]
pub struct DiscordUser(pub User);

impl AsRef<User> for DiscordUser {
	fn as_ref(&self) -> &User { &self.0 }
}

impl<S> FromRequestParts<S> for DiscordUser
where
	CookieConfig: FromRef<S>,
	CachePool: FromRef<S>,
	S: Send + Sync,
{
	type Rejection = Response;

	async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
		let cookie_cfg = CookieConfig::from_ref(state);
		let cache_pool = CachePool::from_ref(state);

		let Some(access_token) = parts.extensions.get::<AccessToken>() else {
			return Err(Error::from(AuthorizationError::MissingAccessTokenCookie).into_response());
		};

		let access_token_lifetime = Duration::seconds(cookie_cfg.access_token_cookie_lifespan);

		let mut conn =
			cache_pool.get().await.map_err(Error::from).map_err(IntoResponse::into_response)?;

		let query_result: Option<String> = conn
			.get(access_token.secret())
			.await
			.map_err(Error::from)
			.map_err(IntoResponse::into_response)?;

		let json_str: String = if let Some(s) = query_result {
			s
		} else {
			cache_user_data(access_token.secret(), access_token_lifetime, &mut conn)
				.await
				.map_err(IntoResponse::into_response)?;

			conn.get(access_token.secret())
				.await
				.map_err(Error::from)
				.map_err(IntoResponse::into_response)?
		};

		let user_data = serde_json::from_str(&json_str)
			.map_err(Error::from)
			.map_err(IntoResponse::into_response)?;

		Ok(user_data)
	}
}

/// Fetch data about the current user from the discord API and store it in the
/// cache
pub async fn cache_user_data(
	token: &str,
	lifetime: Duration,
	conn: &mut CacheConn,
) -> Result<(), Error> {
	debug!("Caching user data...");

	let http = Http::new(&format!("Bearer {token}"));
	let request = Request::new(Route::UserMe, LightMethod::Get);
	let user_data = http.fire::<User>(request).await?;

	// Encode the user object as a json string because the redis json api
	// inspires existential dread
	let data_str = serde_json::to_string(&user_data)?;

	let _: () = conn.set(token, data_str).await?;

	// Set the expiry equal to the access token expiry to ensure no user
	// data is available once authentication has been lost
	let _: () = conn.expire(token, lifetime.whole_seconds()).await?;

	debug!("Cached user data");

	Ok(())
}
