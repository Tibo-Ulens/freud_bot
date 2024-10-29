//! ______                  _______       _
//! |  ___|                | | ___ \     | |
//! | |_ _ __ ___ _   _  __| | |_/ / ___ | |_
//! |  _| '__/ _ \ | | |/ _` | ___ \/ _ \| __|
//! | | | | |  __/ |_| | (_| | |_/ / (_) | |_
//! \_| |_|  \___|\__,_|\__,_\____/ \___/ \__|
//!
//! FreudBot API

#[macro_use]
extern crate tracing;

use std::net::SocketAddr;
use std::str::FromStr;

use axum::extract::FromRef;
use axum::routing::get;
use axum::Router;
use axum_extra::extract::cookie::Key;
use bb8::Pool;
use bb8_redis::RedisConnectionManager;
use diesel::Connection;
use diesel_async::async_connection_wrapper::AsyncConnectionWrapper;
use diesel_async::pooled_connection::AsyncDieselConnectionManager;
use diesel_async::AsyncPgConnection;
use diesel_migrations::{embed_migrations, EmbeddedMigrations, MigrationHarness};
use http::{HeaderValue, Method};
use oauth2::basic::BasicClient;
use oauth2::{AuthUrl, ClientId, ClientSecret, RedirectUrl, TokenUrl};
use tokio::signal;
use tokio::task::spawn_blocking;
use tower_http::cors::CorsLayer;
use tower_http::trace::{DefaultMakeSpan, DefaultOnRequest, DefaultOnResponse, TraceLayer};
use tracing::level_filters::LevelFilter;
use tracing::Level;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::Layer;

pub mod error;
pub mod routes;

use error::Error;
use routes::{login, me, oauth_callback};

type DbPool = Pool<AsyncDieselConnectionManager<AsyncPgConnection>>;
type CachePool = Pool<RedisConnectionManager>;

const MIGRATIONS: EmbeddedMigrations = embed_migrations!();

/// The internal state of the axum app
#[derive(Clone, Debug)]
pub struct AppState {
	oauth_client: BasicClient,
	db_pool:      DbPool,
	cache_pool:   CachePool,
	cookie_key:   Key,
	cookie_cfg:   CookieConfig,
	frontend_url: String,
}

/// The config variables related to session cookies
#[derive(Clone, Debug)]
pub struct CookieConfig {
	cookie_domain: String,

	pkce_verifier_cookie_name: String,
	access_token_cookie_name:  String,
	refresh_token_cookie_name: String,

	pkce_verifier_cookie_lifespan: i64,
	access_token_cookie_lifespan:  i64,
	refresh_token_cookie_lifespan: i64,
}

impl FromRef<AppState> for BasicClient {
	fn from_ref(input: &AppState) -> Self { input.oauth_client.clone() }
}

impl FromRef<AppState> for DbPool {
	fn from_ref(input: &AppState) -> Self { input.db_pool.clone() }
}

impl FromRef<AppState> for CachePool {
	fn from_ref(input: &AppState) -> Self { input.cache_pool.clone() }
}

impl FromRef<AppState> for Key {
	fn from_ref(input: &AppState) -> Self { input.cookie_key.clone() }
}

impl FromRef<AppState> for CookieConfig {
	fn from_ref(input: &AppState) -> Self { input.cookie_cfg.clone() }
}

impl FromRef<AppState> for String {
	fn from_ref(input: &AppState) -> Self { input.frontend_url.clone() }
}

/// Attempt to get the value of an environment variable, panic if it doesn't exist
#[inline]
fn get_env_or_panic<T>(var: &str) -> T
where
	T: FromStr,
	<T as FromStr>::Err: std::fmt::Debug,
{
	std::env::var(var)
		.unwrap_or_else(|_| panic!("MISSING ENVIRONMENT VARIABLE: `{}`", var))
		.parse()
		.unwrap_or_else(|_| panic!("COULD NOT PARSE {}", var))
}

#[tokio::main]
#[instrument]
async fn main() -> Result<(), Error> {
	let console_layer =
		console_subscriber::ConsoleLayer::builder().server_addr(([0, 0, 0, 0], 6669)).spawn();

	let fmt_layer = tracing_subscriber::fmt::layer().pretty().with_filter(LevelFilter::INFO);

	tracing_subscriber::registry().with(console_layer).with(fmt_layer).init();

	info!("creating database threadpool...");
	let db_pool = {
		let db_url = get_env_or_panic::<String>("DB_URL");
		let db_pool_config = AsyncDieselConnectionManager::<AsyncPgConnection>::new(db_url.clone());

		Pool::builder()
			.build(db_pool_config)
			.await
			.expect("COULD NOT CREATE DATABASE CONNECTION POOL")
	};

	info!("creating cache threadpool...");
	let cache_pool = {
		let cache_url = get_env_or_panic::<String>("CACHE_URL");
		let manager = RedisConnectionManager::new(cache_url)
			.expect("COULD NOT CREATE CACHE CONNECTION MANAGER");

		Pool::builder().build(manager).await.expect("COULD NOT CREATE CACHE CONNECTION POOL")
	};

	info!("running migrations...");
	spawn_blocking(move || {
		let db_url = get_env_or_panic::<String>("DB_URL");
		let mut db_conn = AsyncConnectionWrapper::<AsyncPgConnection>::establish(&db_url)
			.expect("COULD NOT CONNECT TO DATABASE FOR MIGRATIONS");

		db_conn.run_pending_migrations(MIGRATIONS).expect("COULD NOT RUN MIGRATIONS");
	})
	.await
	.expect("COULD NOT RUN MIGRATION THREAD");

	info!("creating OAuth2 client...");
	let oauth_client = {
		let oauth_credentials = std::fs::read_to_string("/run/secrets/discord_oauth_credentials")
			.expect("COULD NOT READ DISCORD OAUTH CREDENTIALS");
		let oauth_credentials = oauth_credentials.split("\n").collect::<Vec<&str>>();

		let client_id = oauth_credentials[0].to_string();
		let client_secret = oauth_credentials[1].to_string();

		let redirect_url = get_env_or_panic("REDIRECT_URL");
		let auth_url = get_env_or_panic("AUTH_URL");
		let token_url = get_env_or_panic("TOKEN_URL");

		BasicClient::new(
			ClientId::new(client_id),
			Some(ClientSecret::new(client_secret)),
			AuthUrl::new(auth_url)?,
			Some(TokenUrl::new(token_url)?),
		)
		.set_redirect_uri(RedirectUrl::new(redirect_url)?)
	};

	let cookie_key = Key::generate();

	let cookie_cfg = CookieConfig {
		cookie_domain:                 get_env_or_panic("COOKIE_DOMAIN"),
		pkce_verifier_cookie_name:     get_env_or_panic("PKCE_VERIFIER_COOKIE_NAME"),
		access_token_cookie_name:      get_env_or_panic("ACCESS_TOKEN_COOKIE_NAME"),
		refresh_token_cookie_name:     get_env_or_panic("REFRESH_TOKEN_COOKIE_NAME"),
		pkce_verifier_cookie_lifespan: get_env_or_panic("PKCE_VERIFIER_COOKIE_LIFESPAN"),
		access_token_cookie_lifespan:  get_env_or_panic("ACCESS_TOKEN_COOKIE_LIFESPAN"),
		refresh_token_cookie_lifespan: get_env_or_panic("REFRESH_TOKEN_COOKIE_LIFESPAN"),
	};

	let frontend_url = get_env_or_panic::<String>("FRONTEND_URL");

	info!("creating HTTP server...");
	let app_state = AppState {
		oauth_client,
		db_pool,
		cache_pool,
		cookie_key,
		cookie_cfg,
		frontend_url: frontend_url.clone(),
	};
	let app = Router::new()
		.route("/auth/login", get(login))
		.route("/auth/callback", get(oauth_callback))
		.route("/me", get(me))
		.layer(
			CorsLayer::new()
				.allow_origin(frontend_url.parse::<HeaderValue>().unwrap())
				.allow_methods([Method::GET, Method::POST, Method::PUT])
				.allow_credentials(true),
		)
		.layer(
			TraceLayer::new_for_http()
				.make_span_with(DefaultMakeSpan::new().include_headers(true).level(Level::INFO))
				.on_request(DefaultOnRequest::new().level(Level::INFO))
				.on_response(DefaultOnResponse::new().include_headers(true).level(Level::INFO)),
		)
		.with_state(app_state);

	info!("starting HTTP server...");
	let addr = SocketAddr::from(([0, 0, 0, 0], 80));
	let listener = tokio::net::TcpListener::bind(addr).await.expect("COULD NOT BIND TCP LISTENER");

	axum::serve(listener, app).with_graceful_shutdown(shutdown_signal_handler()).await.unwrap();

	Ok(())
}

/// Creates a pending future which completes when a shutdown signal is received
async fn shutdown_signal_handler() {
	let ctrl_c = async { signal::ctrl_c().await.expect("FAILED TO INSTALL CTRL+C HANDLER") };

	#[cfg(unix)]
	let terminate = async {
		signal::unix::signal(signal::unix::SignalKind::terminate())
			.expect("FAILED TO INSTALL TERMINATION SIGNAL HANDLER")
			.recv()
			.await;
	};

	#[cfg(not(unix))]
	let terminate = std::future::pending::<()>();

	tokio::select! {
		_ = ctrl_c => {},
		_ = terminate => {},
	};

	info!("shutting down...");
}
