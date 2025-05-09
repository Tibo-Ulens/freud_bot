//! Middleware to authorize users and store user data on the request objects

use std::pin::Pin;
use std::task::{Context, Poll};

use axum::RequestExt;
use axum::body::Body;
use axum::extract::Request;
use axum::http::Response;
use axum::response::IntoResponse;
use axum_extra::extract::PrivateCookieJar;
use oauth2::{AccessToken, RefreshToken, Scope, TokenResponse};
use reqwest::{ClientBuilder, redirect};
use time::Duration;
use tower::{Layer, Service};

use crate::error::AuthorizationError;
use crate::routes::{normalise_cookie, store_token_cookies};
use crate::{AppState, Error};

/// Middleware that guarantees the client has a valid discord access token (and
/// refresh token if provided)
///
/// If only a refresh token is found it is exchanged for 2 new tokens
#[derive(Clone)]
pub struct AuthLayer {
	state: AppState,
}

impl AuthLayer {
	#[must_use]
	pub fn new(state: AppState) -> Self { Self { state } }
}

impl<S> Layer<S> for AuthLayer {
	type Service = AuthMiddleware<S>;

	fn layer(&self, inner: S) -> Self::Service {
		AuthMiddleware { inner, state: self.state.clone() }
	}
}

#[derive(Clone)]
pub struct AuthMiddleware<S> {
	inner: S,
	state: AppState,
}

impl<S> Service<Request<Body>> for AuthMiddleware<S>
where
	S: Service<Request, Response = Response<Body>> + Clone + Send + 'static,
	S::Future: Send + 'static,
{
	type Error = S::Error;
	type Future =
		Pin<Box<dyn Future<Output = Result<Self::Response, Self::Error>> + Send + 'static>>;
	type Response = S::Response;

	fn poll_ready(&mut self, cx: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
		self.inner.poll_ready(cx)
	}

	#[instrument(skip_all)]
	fn call(&mut self, mut req: Request<Body>) -> Self::Future {
		let cloned_inner = self.inner.clone();
		let mut inner = std::mem::replace(&mut self.inner, cloned_inner);

		let state = self.state.clone();

		Box::pin(async move {
			let mut jar =
				req.extract_parts_with_state::<PrivateCookieJar, _>(&state).await.unwrap();

			let access_token_cookie =
				if let Some(c) = jar.get(&state.cookie_cfg.access_token_cookie_name) {
					c
				} else {
					warn!("Request missing valid access token cookie");

					jar = match try_exchange_refresh_token(jar, &state).await {
						Ok(j) => j,
						Err(e) => return Ok(e.into_response()),
					};

					jar.get(&state.cookie_cfg.access_token_cookie_name).unwrap()
				};

			let access_token = AccessToken::new(access_token_cookie.value().to_string());

			req.extensions_mut().insert(access_token);

			inner.call(req).await.map(|res| (jar, res).into_response())
		})
	}
}

#[instrument(skip_all)]
async fn try_exchange_refresh_token(
	jar: PrivateCookieJar,
	state: &AppState,
) -> Result<PrivateCookieJar, Error> {
	let Some(mut refresh_token_cookie) = jar.get(&state.cookie_cfg.refresh_token_cookie_name)
	else {
		return Err(AuthorizationError::MissingRefreshTokenCookie.into());
	};

	let refresh_token = RefreshToken::new(refresh_token_cookie.value().to_string());

	normalise_cookie(&mut refresh_token_cookie, &state.cookie_cfg);
	let jar = jar.remove(refresh_token_cookie);

	let client = ClientBuilder::new().redirect(redirect::Policy::none()).build()?;

	debug!("Exchanging refresh token...");

	let token = state
		.oauth_client
		.exchange_refresh_token(&refresh_token)
		.add_scope(Scope::new("identify".to_string()))
		.request_async(&client)
		.await
		.map_err(|e| AuthorizationError::RequestTokenError(anyhow::Error::from(e)))?;

	#[allow(clippy::cast_possible_wrap)]
	let access_token_expiry = token
		.expires_in()
		.map_or(Duration::seconds(state.cookie_cfg.access_token_cookie_lifespan), |d| {
			Duration::seconds(d.as_secs() as i64)
		});

	let jar = store_token_cookies(&token, jar, &state.cookie_cfg, access_token_expiry);

	debug!("Exchanged refresh token");

	Ok(jar)
}
