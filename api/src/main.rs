#[macro_use]
extern crate tracing;

use std::net::SocketAddr;
use std::str::FromStr;

use axum::Router;
use axum::extract::FromRef;
use axum::routing::{get, post};
use axum_extra::extract::cookie::Key;
use diesel_async::AsyncPgConnection;
use diesel_async::pooled_connection::AsyncDieselConnectionManager;
use lettre::Address;
use mailer::Mailer;
use middleware::AuthLayer;
use oauth2::basic::BasicClient;
use oauth2::{AuthUrl, ClientId, ClientSecret, EndpointNotSet, EndpointSet, RedirectUrl, TokenUrl};
use tokio::signal;
use tower_http::compression::CompressionLayer;
use tower_http::timeout::TimeoutLayer;
use tower_http::trace::{DefaultMakeSpan, DefaultOnRequest, DefaultOnResponse, TraceLayer};
use tracing::Level;
use tracing::level_filters::LevelFilter;
use tracing_subscriber::Layer;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;

pub mod error;
pub mod extractors;
pub mod mailer;
pub mod middleware;
pub mod models;
pub mod routes;
pub mod schema;

use error::Error;
use routes::{confirm_verify, is_verified, login, logout, me, oauth_callback, request_verify};

type DbPool = diesel_async::pooled_connection::deadpool::Pool<AsyncPgConnection>;
type CachePool = deadpool_redis::Pool;
type AmqpPool = deadpool_lapin::Pool;

type DbConn = diesel_async::pooled_connection::deadpool::Object<AsyncPgConnection>;
type CacheConn = deadpool_redis::Connection;
type AmqpConn = deadpool_lapin::Connection;

type SetBasicClient =
	BasicClient<EndpointSet, EndpointNotSet, EndpointNotSet, EndpointNotSet, EndpointSet>;

/// The internal state of the axum app
#[derive(Clone)]
pub struct AppState {
	oauth_client: SetBasicClient,
	mailer:       Mailer,

	db_pool:    DbPool,
	cache_pool: CachePool,
	amqp_pool:  AmqpPool,

	cookie_key: Key,
	cookie_cfg: CookieConfig,

	base_url: String,
}

/// The config variables related to session cookies
#[derive(Clone, Debug)]
pub struct CookieConfig {
	cookie_domain: String,

	pkce_verifier_cookie_name:  String,
	csrf_token_cookie_name:     String,
	oauth_redirect_cookie_name: String,
	access_token_cookie_name:   String,
	refresh_token_cookie_name:  String,

	pkce_verifier_cookie_lifespan:  i64,
	csrf_token_cookie_lifespan:     i64,
	oauth_redirect_cookie_lifespan: i64,
	access_token_cookie_lifespan:   i64,
	refresh_token_cookie_lifespan:  i64,
}

impl FromRef<AppState> for SetBasicClient {
	fn from_ref(input: &AppState) -> Self { input.oauth_client.clone() }
}

impl FromRef<AppState> for Mailer {
	fn from_ref(input: &AppState) -> Self { input.mailer.clone() }
}

impl FromRef<AppState> for DbPool {
	fn from_ref(input: &AppState) -> Self { input.db_pool.clone() }
}

impl FromRef<AppState> for CachePool {
	fn from_ref(input: &AppState) -> Self { input.cache_pool.clone() }
}

impl FromRef<AppState> for AmqpPool {
	fn from_ref(input: &AppState) -> Self { input.amqp_pool.clone() }
}

impl FromRef<AppState> for Key {
	fn from_ref(input: &AppState) -> Self { input.cookie_key.clone() }
}

impl FromRef<AppState> for CookieConfig {
	fn from_ref(input: &AppState) -> Self { input.cookie_cfg.clone() }
}

impl FromRef<AppState> for String {
	fn from_ref(input: &AppState) -> Self { input.base_url.clone() }
}

/// Attempt to get the value of an environment variable, panic if it doesn't
/// exist
#[inline]
fn get_env_or_panic<T>(var: &str) -> T
where
	T: FromStr,
	<T as FromStr>::Err: std::fmt::Debug,
{
	std::env::var(var)
		.unwrap_or_else(|_| panic!("MISSING ENVIRONMENT VARIABLE: `{var}`"))
		.parse()
		.unwrap_or_else(|_| panic!("COULD NOT PARSE `{var}`"))
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

		diesel_async::pooled_connection::deadpool::Pool::builder(db_pool_config)
			.build()
			.expect("COULD NOT CREATE DATABASE CONNECTION POOL")
	};

	info!("creating cache threadpool...");
	let cache_pool = {
		let cache_url = get_env_or_panic::<String>("CACHE_URL");
		let cache_cfg = deadpool_redis::Config::from_url(cache_url);

		cache_cfg
			.create_pool(Some(deadpool_redis::Runtime::Tokio1))
			.expect("COULD NOT CREATE CACHE CONNECTION POOL")
	};

	info!("creating AMQP threadpool...");
	let amqp_pool = {
		let amqp_cfg = deadpool_lapin::Config {
			url: Some(get_env_or_panic("AMQP_URL")),
			..Default::default()
		};

		amqp_cfg
			.create_pool(Some(deadpool_lapin::Runtime::Tokio1))
			.expect("COULD NOT CREATE AMQP POOL")
	};

	info!("creating OAuth2 client...");
	let oauth_client = {
		let oauth_credentials = std::fs::read_to_string("/run/secrets/discord_oauth_credentials")
			.expect("COULD NOT READ DISCORD OAUTH CREDENTIALS");
		let oauth_credentials = oauth_credentials.split('\n').collect::<Vec<&str>>();

		let client_id = oauth_credentials[0].to_string();
		let client_secret = oauth_credentials[1].to_string();

		let redirect_url = get_env_or_panic("REDIRECT_URL");
		let auth_url = get_env_or_panic("AUTH_URL");
		let token_url = get_env_or_panic("TOKEN_URL");

		BasicClient::new(ClientId::new(client_id))
			.set_client_secret(ClientSecret::new(client_secret))
			.set_auth_uri(AuthUrl::new(auth_url)?)
			.set_token_uri(TokenUrl::new(token_url)?)
			.set_redirect_uri(RedirectUrl::new(redirect_url)?)
	};

	info!("creating mailer...");
	let mailer = {
		let gmail_smtp_credentials = std::fs::read_to_string("/run/secrets/gmail_smtp_credentials")
			.expect("COULD NOT READ GMAIL SMTP CREDENTIALS");
		let gmail_smtp_credentials = gmail_smtp_credentials.split('\n').collect::<Vec<&str>>();

		let sender = gmail_smtp_credentials[0].parse::<Address>().expect("INVALID EMAIL ADDRESS");
		let password = gmail_smtp_credentials[1].to_string();

		Mailer::new(sender, password)
	};

	let cookie_key = Key::generate();

	let cookie_cfg = CookieConfig {
		cookie_domain:                  get_env_or_panic("COOKIE_DOMAIN"),
		pkce_verifier_cookie_name:      get_env_or_panic("PKCE_VERIFIER_COOKIE_NAME"),
		csrf_token_cookie_name:         get_env_or_panic("CSRF_TOKEN_COOKIE_NAME"),
		oauth_redirect_cookie_name:     get_env_or_panic("OAUTH_REDIRECT_COOKIE_NAME"),
		access_token_cookie_name:       get_env_or_panic("ACCESS_TOKEN_COOKIE_NAME"),
		refresh_token_cookie_name:      get_env_or_panic("REFRESH_TOKEN_COOKIE_NAME"),
		pkce_verifier_cookie_lifespan:  get_env_or_panic("PKCE_VERIFIER_COOKIE_LIFESPAN"),
		csrf_token_cookie_lifespan:     get_env_or_panic("CSRF_TOKEN_COOKIE_LIFESPAN"),
		oauth_redirect_cookie_lifespan: get_env_or_panic("OAUTH_REDIRECT_COOKIE_LIFESPAN"),
		access_token_cookie_lifespan:   get_env_or_panic("ACCESS_TOKEN_COOKIE_LIFESPAN"),
		refresh_token_cookie_lifespan:  get_env_or_panic("REFRESH_TOKEN_COOKIE_LIFESPAN"),
	};

	let base_url = get_env_or_panic::<String>("BASE_URL");

	info!("creating HTTP server...");
	let app_state = AppState {
		oauth_client,
		mailer,
		db_pool,
		cache_pool,
		amqp_pool,
		cookie_key,
		cookie_cfg,
		base_url,
	};
	let app = Router::new()
		.route("/auth/login", get(login))
		.route("/auth/callback", get(oauth_callback))
		.route("/auth/logout", get(logout))
		.merge(
			Router::new()
				.route("/me", get(me))
				.route("/request_verify", post(request_verify))
				.route("/verify/{confirmation_code}", post(confirm_verify))
				.route("/is_verified", get(is_verified))
				.route_layer(AuthLayer::new(app_state.clone())),
		)
		.layer(TimeoutLayer::new(std::time::Duration::from_secs(5)))
		.layer(CompressionLayer::new())
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
	let ctrl_c = async {
		signal::ctrl_c().await.expect("FAILED TO INSTALL CTRL+C HANDLER");
	};

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
		() = ctrl_c => {},
		() = terminate => {},
	};

	info!("shutting down...");
}
