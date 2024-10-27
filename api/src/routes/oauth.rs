//! OAuth2 routes and datatypes

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
	Scope,
	TokenResponse,
};
use redis::AsyncCommands;
use serde::{Deserialize, Serialize};
use time::Duration;
use uuid::Uuid;

use crate::error::{AuthorizationError, Error};
use crate::{CachePool, CookieConfig};

/// The user data that's returned from the Discord OAuth API and which is also
/// needed within this application
///
/// TODO: write extractor that redirects if invalid cookies are detected
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct DiscordUser {
	id:       String,
	username: String,
	avatar:   Option<String>,
}

fn make_cookie(name: String, value: String, domain: String, lifespan: Duration) -> Cookie<'static> {
	let mut cookie = Cookie::new(name, value);

	cookie.set_domain(domain);
	cookie.set_max_age(lifespan);
	cookie.set_http_only(true);
	cookie.set_secure(true);
	cookie.set_same_site(SameSite::Lax);

	cookie
}

#[instrument]
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

#[instrument]
pub async fn oauth_callback(
	Query(query): Query<AuthRequest>,
	State(oauth_client): State<BasicClient>,
	State(cache_pool): State<CachePool>,
	State(cookie_cfg): State<CookieConfig>,
	jar: PrivateCookieJar,
) -> Result<impl IntoResponse, Error> {
	// Read the PKCE verifier UUID from the cookie and use it to look up the
	// verifier in redis
	let pkce_verifier_cookie = jar
		.get(&cookie_cfg.pkce_verifier_cookie_name)
		.ok_or_else(|| AuthorizationError::MissingPKCEVerifierCookie)?;

	let pkce_verifier_uuid = pkce_verifier_cookie.value().to_string();

	// PKCE verifiers are single use so delete the cookie afterwards
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

	// Fetch user details from the discord API to store in the session data
	// cookie
	let client = reqwest::Client::new();
	let user_data: DiscordUser = client
		.get("https://discordapp.com/api/users/@me")
		.bearer_auth(token.access_token().secret())
		.send()
		.await?
		.json::<DiscordUser>()
		.await?;

	let access_cookie = make_cookie(
		cookie_cfg.access_token_cookie_name.to_string(),
		token.access_token().secret().to_string(),
		cookie_cfg.cookie_domain.clone(),
		token
			.expires_in()
			.map(|d| Duration::seconds(d.as_secs() as i64))
			.unwrap_or(Duration::seconds(cookie_cfg.access_token_cookie_lifespan)),
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

	let userdata_cookie = make_cookie(
		cookie_cfg.session_data_cookie_name.to_string(),
		serde_json::to_string(&user_data).unwrap(),
		cookie_cfg.cookie_domain,
		Duration::seconds(cookie_cfg.session_data_cookie_lifespan),
	);

	jar = jar.add(userdata_cookie);

	Ok((jar, Redirect::to("/")))
}
