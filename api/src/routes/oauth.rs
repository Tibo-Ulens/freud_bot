//! `OAuth2` routes and datatypes

use std::collections::HashMap;

use axum::extract::{Query, State};
use axum::response::{IntoResponse, Redirect};
use axum_extra::extract::PrivateCookieJar;
use axum_extra::extract::cookie::{Cookie, SameSite};
use deadpool_redis::redis::AsyncCommands;
use oauth2::basic::BasicTokenType;
use oauth2::reqwest::{ClientBuilder, redirect};
use oauth2::{
	AuthorizationCode,
	CsrfToken,
	EmptyExtraTokenFields,
	PkceCodeChallenge,
	PkceCodeVerifier,
	Scope,
	StandardTokenResponse,
	TokenResponse,
};
use serde::Deserialize;
use time::Duration;
use uuid::Uuid;

use crate::error::{AuthorizationError, Error};
use crate::extractors::discord::cache_user_data;
use crate::{CachePool, CookieConfig, SetBasicClient};

#[must_use]
pub fn make_cookie(
	name: String,
	value: String,
	domain: String,
	lifespan: Duration,
) -> Cookie<'static> {
	let mut cookie = Cookie::new(name, value);

	cookie.set_domain(domain);
	cookie.set_max_age(lifespan);
	cookie.set_http_only(true);
	cookie.set_secure(true);
	cookie.set_same_site(SameSite::Lax);
	cookie.set_path("/");

	cookie
}

/// For some reason axum-extra decided that cookies that are retrieved from the
/// jar don't need to retain their attributes, so these have to be re-added in
/// order to remove the cookie from the jar
pub fn normalise_cookie<'c, 'r>(
	cookie: &'r mut Cookie<'c>,
	cookie_cfg: &CookieConfig,
) -> &'r Cookie<'c> {
	cookie.set_domain(cookie_cfg.cookie_domain.clone());
	cookie.set_http_only(true);
	cookie.set_secure(true);
	cookie.set_same_site(SameSite::Lax);
	cookie.set_path("/");

	cookie
}

#[must_use]
pub fn store_token_cookies(
	token: &StandardTokenResponse<EmptyExtraTokenFields, BasicTokenType>,
	mut jar: PrivateCookieJar,
	cookie_cfg: &CookieConfig,
	lifetime: Duration,
) -> PrivateCookieJar {
	let access_cookie = make_cookie(
		cookie_cfg.access_token_cookie_name.to_string(),
		token.access_token().secret().to_string(),
		cookie_cfg.cookie_domain.clone(),
		lifetime,
	);

	jar = jar.add(access_cookie);

	if let Some(refresh_token) = token.refresh_token() {
		let refresh_cookie = make_cookie(
			cookie_cfg.refresh_token_cookie_name.to_string(),
			refresh_token.secret().to_string(),
			cookie_cfg.cookie_domain.clone(),
			Duration::seconds(cookie_cfg.refresh_token_cookie_lifespan),
		);

		jar = jar.add(refresh_cookie);
	}

	jar
}

#[instrument(skip_all)]
pub async fn login(
	State(oauth_client): State<SetBasicClient>,
	State(cache_pool): State<CachePool>,
	State(cookie_cfg): State<CookieConfig>,
	State(frontend_url): State<String>,
	Query(params): Query<HashMap<String, String>>,
	jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	// Generate a UUID alongside the PKCE codes so the verifier can be stored
	// in redis to then be retrieved later in the callback route
	// The UUID acts as a unique key to store the verifier
	let (pkce_challenge, pkce_verifier) = PkceCodeChallenge::new_random_sha256();
	let pkce_verifier_uuid = Uuid::now_v7();

	let (auth_url, csrf_token) = oauth_client
		.authorize_url(CsrfToken::new_random)
		.set_pkce_challenge(pkce_challenge)
		.add_scope(Scope::new("identify".to_string()))
		.url();

	let mut conn = cache_pool.get().await?;
	let _: () = conn.set(pkce_verifier_uuid.to_string(), pkce_verifier.secret()).await?;

	let pkce_verifier_uuid_cookie = make_cookie(
		cookie_cfg.pkce_verifier_cookie_name,
		pkce_verifier_uuid.to_string(),
		cookie_cfg.cookie_domain.clone(),
		Duration::seconds(cookie_cfg.pkce_verifier_cookie_lifespan),
	);

	let csrf_token_cookie = make_cookie(
		cookie_cfg.csrf_token_cookie_name,
		csrf_token.into_secret(),
		cookie_cfg.cookie_domain.clone(),
		Duration::seconds(cookie_cfg.csrf_token_cookie_lifespan),
	);

	let redirect_uri = params.get("redirect").unwrap_or(&frontend_url);
	let oauth_redirect_cookie = make_cookie(
		cookie_cfg.oauth_redirect_cookie_name,
		redirect_uri.to_string(),
		cookie_cfg.cookie_domain,
		Duration::seconds(cookie_cfg.oauth_redirect_cookie_lifespan),
	);

	let jar = jar.add(pkce_verifier_uuid_cookie);
	let jar = jar.add(csrf_token_cookie);
	let jar = jar.add(oauth_redirect_cookie);

	Ok((jar, Redirect::to(auth_url.as_ref())))
}

#[derive(Clone, Debug, Deserialize)]
#[allow(dead_code)]
pub struct AuthRequest {
	code:  String,
	state: String,
}

#[instrument(skip(oauth_client, cache_pool, cookie_cfg, frontend_url, jar))]
pub async fn oauth_callback(
	Query(query): Query<AuthRequest>,
	State(oauth_client): State<SetBasicClient>,
	State(cache_pool): State<CachePool>,
	State(cookie_cfg): State<CookieConfig>,
	State(frontend_url): State<String>,
	mut jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	let mut csrf_token_cookie = jar
		.get(&cookie_cfg.csrf_token_cookie_name)
		.ok_or_else(|| AuthorizationError::MissingCSRFTokenCookie)?;

	let csrf_token = csrf_token_cookie.value();

	if csrf_token != query.state {
		return Err(AuthorizationError::IncorrectCSRFToken)?;
	}

	normalise_cookie(&mut csrf_token_cookie, &cookie_cfg);
	jar = jar.remove(csrf_token_cookie);

	// Read the PKCE verifier UUID from the cookie and use it to look up the
	// verifier in redis
	let mut pkce_verifier_cookie = jar
		.get(&cookie_cfg.pkce_verifier_cookie_name)
		.ok_or_else(|| AuthorizationError::MissingPKCEVerifierCookie)?;

	let pkce_verifier_uuid = pkce_verifier_cookie.value().to_string();

	normalise_cookie(&mut pkce_verifier_cookie, &cookie_cfg);
	jar = jar.remove(pkce_verifier_cookie);

	let mut conn = cache_pool.get().await?;

	// PKCE verifiers are single use so delete the verifier afterwards
	let pkce_verifier_secret: String = conn.get(&pkce_verifier_uuid).await?;
	let _: () = conn.del(&pkce_verifier_uuid).await?;

	let pkce_verifier = PkceCodeVerifier::new(pkce_verifier_secret);

	let client = ClientBuilder::new().redirect(redirect::Policy::none()).build()?;

	let token = oauth_client
		.exchange_code(AuthorizationCode::new(query.code))
		.set_pkce_verifier(pkce_verifier)
		.request_async(&client)
		.await
		.map_err(|e| AuthorizationError::RequestTokenError(anyhow::Error::from(e)))?;

	#[allow(clippy::cast_possible_wrap)]
	let access_token_expiry = token
		.expires_in()
		.map_or(Duration::seconds(cookie_cfg.access_token_cookie_lifespan), |d| {
			Duration::seconds(d.as_secs() as i64)
		});

	cache_user_data(token.access_token().secret(), access_token_expiry, &mut conn).await?;

	jar = store_token_cookies(&token, jar, &cookie_cfg, access_token_expiry);

	let oauth_redirect_cookie = jar.get(&cookie_cfg.oauth_redirect_cookie_name);

	let redirect = match oauth_redirect_cookie {
		Some(mut c) => {
			let redirect = c.value().to_string();

			normalise_cookie(&mut c, &cookie_cfg);
			jar = jar.remove(c);

			redirect
		},
		None => frontend_url,
	};

	Ok((jar, Redirect::to(&redirect)))
}

pub async fn logout(
	State(cookie_cfg): State<CookieConfig>,
	State(frontend_url): State<String>,
	mut jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	if let Some(mut access_token_cookie) = jar.get(&cookie_cfg.access_token_cookie_name) {
		normalise_cookie(&mut access_token_cookie, &cookie_cfg);
		jar = jar.remove(access_token_cookie);
	}

	if let Some(mut refresh_token_cookie) = jar.get(&cookie_cfg.refresh_token_cookie_name) {
		normalise_cookie(&mut refresh_token_cookie, &cookie_cfg);
		jar = jar.remove(refresh_token_cookie);
	}

	Ok((jar, Redirect::to(&frontend_url)))
}
