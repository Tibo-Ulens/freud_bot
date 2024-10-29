//! OAuth2 routes and datatypes
//!
//! TODO: add a route to exchange refresh tokens

use axum::extract::{Query, State};
use axum::response::{IntoResponse, Redirect};
use axum_extra::extract::cookie::{Cookie, SameSite};
use axum_extra::extract::PrivateCookieJar;
use oauth2::basic::BasicClient;
use oauth2::reqwest::async_http_client;
use oauth2::{
	AuthorizationCode,
	CsrfToken,
	PkceCodeChallenge,
	PkceCodeVerifier,
	RefreshToken,
	Scope,
	TokenResponse,
};
use redis::AsyncCommands;
use serde::Deserialize;
use time::Duration;
use uuid::Uuid;

use crate::error::{AuthorizationError, Error};
use crate::routes::DiscordUser;
use crate::{CachePool, CookieConfig};

fn make_cookie(name: String, value: String, domain: String, lifespan: Duration) -> Cookie<'static> {
	let mut cookie = Cookie::new(name, value);

	cookie.set_domain(domain);
	cookie.set_max_age(lifespan);
	cookie.set_http_only(true);
	cookie.set_secure(true);
	cookie.set_same_site(SameSite::Lax);
	cookie.set_path("/");

	cookie
}

#[instrument(skip_all)]
pub async fn login(
	State(oauth_client): State<BasicClient>,
	State(cache_pool): State<CachePool>,
	State(cookie_cfg): State<CookieConfig>,
	jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	// Generate a UUID alongside the PKCE codes so the verifier can be stored
	// in redis to then be retrieved later in the callback route
	// The UUID acts as a unique key to store the verifier
	let (pkce_challenge, pkce_verifier) = PkceCodeChallenge::new_random_sha256();
	let pkce_verifier_uuid = Uuid::now_v7();

	// TODO: figure out CSRF tokens
	let (auth_url, _csrf_token) = oauth_client
		.authorize_url(CsrfToken::new_random)
		.set_pkce_challenge(pkce_challenge)
		.add_scope(Scope::new("identify".to_string()))
		.url();

	{
		let mut conn = cache_pool.get().await?;

		let _: () =
			conn.set(pkce_verifier_uuid.to_string(), pkce_verifier.secret().to_string()).await?;
	}

	let pkce_verifier_uuid_cookie = make_cookie(
		cookie_cfg.pkce_verifier_cookie_name,
		pkce_verifier_uuid.to_string(),
		cookie_cfg.cookie_domain,
		Duration::seconds(cookie_cfg.pkce_verifier_cookie_lifespan),
	);

	let jar = jar.add(pkce_verifier_uuid_cookie);

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
	State(oauth_client): State<BasicClient>,
	State(cache_pool): State<CachePool>,
	State(cookie_cfg): State<CookieConfig>,
	State(frontend_url): State<String>,
	jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	// Read the PKCE verifier UUID from the cookie and use it to look up the
	// verifier in redis
	let mut pkce_verifier_cookie = jar
		.get(&cookie_cfg.pkce_verifier_cookie_name)
		.ok_or_else(|| AuthorizationError::MissingPKCEVerifierCookie)?;

	let pkce_verifier_uuid = pkce_verifier_cookie.value().to_string();

	// PKCE verifiers are single use so delete the cookie afterwards
	//
	// For some reason axum-extra decided that cookies that are retrieved from
	// the jar don't need to retain their attributes, so these have to be
	// re-added in order for the removal to actually work
	pkce_verifier_cookie.set_domain(cookie_cfg.cookie_domain.clone());
	pkce_verifier_cookie.set_http_only(true);
	pkce_verifier_cookie.set_secure(true);
	pkce_verifier_cookie.set_same_site(SameSite::Lax);
	pkce_verifier_cookie.set_path("/");

	let mut jar = jar.remove(pkce_verifier_cookie);

	let pkce_verifier_secret: String = {
		let mut conn = cache_pool.get().await?;

		let secret: String = conn.get(&pkce_verifier_uuid).await?;

		// PKCE verifiers are single use so delete the verifier afterwards
		let _: () = conn.del(&pkce_verifier_uuid).await?;

		secret
	};

	let pkce_verifier = PkceCodeVerifier::new(pkce_verifier_secret);

	let token = oauth_client
		.exchange_code(AuthorizationCode::new(query.code))
		.set_pkce_verifier(pkce_verifier)
		.request_async(async_http_client)
		.await
		.map_err(|e| AuthorizationError::RequestTokenError(anyhow::Error::from(e)))?;

	let access_token_expiry = token
		.expires_in()
		.map(|d| Duration::seconds(d.as_secs() as i64))
		.unwrap_or(Duration::seconds(cookie_cfg.access_token_cookie_lifespan));

	// Fetch user details from the discord API to store in the cache
	let client = reqwest::Client::new();
	let user_data: DiscordUser = client
		.get("https://discordapp.com/api/users/@me")
		.bearer_auth(token.access_token().secret())
		.send()
		.await?
		.json::<DiscordUser>()
		.await?;

	{
		let mut conn = cache_pool.get().await?;

		// Encode the user object as a json string because the redis json api
		// inspires existential dread
		let _: () =
			conn.set(token.access_token().secret(), serde_json::to_string(&user_data)?).await?;

		// Set the expiry equal to the access token expiry to ensure no user
		// data is available once authentication has been lost
		let _: () =
			conn.expire(token.access_token().secret(), access_token_expiry.whole_seconds()).await?;
	}

	let access_cookie = make_cookie(
		cookie_cfg.access_token_cookie_name.to_string(),
		token.access_token().secret().to_string(),
		cookie_cfg.cookie_domain.clone(),
		access_token_expiry,
	);

	jar = jar.add(access_cookie);

	if let Some(refresh_token) = token.refresh_token() {
		let refresh_cookie = make_cookie(
			cookie_cfg.refresh_token_cookie_name.to_string(),
			refresh_token.secret().to_string(),
			cookie_cfg.cookie_domain.clone(),
			Duration::seconds(cookie_cfg.refresh_token_cookie_lifespan),
		);

		jar = jar.add(refresh_cookie)
	}

	Ok((jar, Redirect::to(&frontend_url)))
}

#[instrument(skip_all)]
pub async fn oauth_refresh(
	State(oauth_client): State<BasicClient>,
	State(cookie_cfg): State<CookieConfig>,
	State(cache_pool): State<CachePool>,
	State(frontend_url): State<String>,
	jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	let mut refresh_token_cookie = jar
		.get(&cookie_cfg.refresh_token_cookie_name)
		.ok_or_else(|| AuthorizationError::MissingRefreshTokenCookie)?;

	let refresh_token = RefreshToken::new(refresh_token_cookie.value().to_string());

	// For some reason axum-extra decided that cookies that are retrieved from
	// the jar don't need to retain their attributes, so these have to be
	// re-added in order for the removal to actually work
	refresh_token_cookie.set_domain(cookie_cfg.cookie_domain.clone());
	refresh_token_cookie.set_http_only(true);
	refresh_token_cookie.set_secure(true);
	refresh_token_cookie.set_same_site(SameSite::Lax);
	refresh_token_cookie.set_path("/");

	let mut jar = jar.remove(refresh_token_cookie);

	let token = oauth_client
		.exchange_refresh_token(&refresh_token)
		.add_scope(Scope::new("identify".to_string()))
		.request_async(async_http_client)
		.await
		.map_err(|e| AuthorizationError::RequestTokenError(anyhow::Error::from(e)))?;

	let access_token_expiry = token
		.expires_in()
		.map(|d| Duration::seconds(d.as_secs() as i64))
		.unwrap_or(Duration::seconds(cookie_cfg.access_token_cookie_lifespan));

	// Fetch user details from the discord API to store in the cache
	let client = reqwest::Client::new();
	let user_data: DiscordUser = client
		.get("https://discordapp.com/api/users/@me")
		.bearer_auth(token.access_token().secret())
		.send()
		.await?
		.json::<DiscordUser>()
		.await?;

	{
		let mut conn = cache_pool.get().await?;

		// Encode the user object as a json string because the redis json api
		// inspires existential dread
		let _: () =
			conn.set(token.access_token().secret(), serde_json::to_string(&user_data)?).await?;

		// Set the expiry equal to the access token expiry to ensure no user
		// data is available once authentication has been lost
		let _: () =
			conn.expire(token.access_token().secret(), access_token_expiry.whole_seconds()).await?;
	}

	let access_cookie = make_cookie(
		cookie_cfg.access_token_cookie_name.to_string(),
		token.access_token().secret().to_string(),
		cookie_cfg.cookie_domain.clone(),
		access_token_expiry,
	);

	jar = jar.add(access_cookie);

	if let Some(refresh_token) = token.refresh_token() {
		let refresh_cookie = make_cookie(
			cookie_cfg.refresh_token_cookie_name.to_string(),
			refresh_token.secret().to_string(),
			cookie_cfg.cookie_domain.clone(),
			Duration::seconds(cookie_cfg.refresh_token_cookie_lifespan),
		);

		jar = jar.add(refresh_cookie)
	}

	todo!("this throws 500 errors client-side");
	Ok((jar, Redirect::to(&frontend_url)))
}
