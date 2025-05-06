//! Types and impls related to error handling

use std::collections::HashMap;
use std::sync::LazyLock;

use axum::response::{IntoResponse, Response};
use bb8::RunError;
use diesel::result::DatabaseErrorKind;
use diesel_async::pooled_connection::deadpool::PoolError;
use http::{StatusCode, header};
use redis::RedisError;
use thiserror::Error;

/// Top level error type
#[derive(Debug, Error)]
pub enum Error {
	#[error("Internal Server Error")]
	InternalError,

	#[error(transparent)]
	AuthorizationError(#[from] AuthorizationError),

	#[error("{0}")]
	Duplicate(String),

	#[error("not found - {0}")]
	NotFound(String),

	#[error("{0}")]
	ValidationError(String),
}

/// Details about internal errors should not be show to end users, so log a
/// warning and then generate an opaque type
impl From<InternalError> for Error {
	fn from(_: InternalError) -> Self {
		error!("!!! internal error !!!");

		Self::InternalError
	}
}

impl IntoResponse for Error {
	fn into_response(self) -> Response {
		error!("{}", self);

		let body = self.to_string();

		let status_code = match self {
			Self::InternalError => StatusCode::INTERNAL_SERVER_ERROR,
			Self::AuthorizationError(_) => StatusCode::UNAUTHORIZED,
			Self::NotFound(_) => StatusCode::NOT_FOUND,
			Self::ValidationError(_) => StatusCode::UNPROCESSABLE_ENTITY,
			Self::Duplicate(_) => StatusCode::CONFLICT,
		};

		Response::builder()
			.header(header::CONTENT_TYPE, "text/plain; charset=utf-8")
			.status(status_code)
			.body(body.into())
			.unwrap()
	}
}

#[derive(Debug, Error)]
pub enum InternalError {
	#[error("reqwest error -- {0:?}")]
	ReqwestError(#[from] reqwest::Error),

	#[error("database pool error -- {0:?}")]
	PoolError(#[from] PoolError),

	#[error("cache pool error -- {0:?}")]
	Bb8RedisError(#[from] RunError<RedisError>),

	#[error("cache error -- {0:?}")]
	CacheError(#[from] RedisError),

	#[error("url parsing error -- {0:?}")]
	UrlParseError(#[from] oauth2::url::ParseError),

	#[error("JSON (de)serialization error -- {0:?}")]
	SerdeJsonError(#[from] serde_json::Error),

	#[error("database error -- {0:?}")]
	DatabaseError(diesel::result::Error),
}

#[derive(Debug, Error)]
pub enum AuthorizationError {
	#[error("Missing PKCE verifier cookie")]
	MissingPKCEVerifierCookie,

	#[error("Missing access token cookie")]
	MissingAccessTokenCookie,

	#[error("Missing refresh token cookie")]
	MissingRefreshTokenCookie,

	#[error(transparent)]
	RequestTokenError(#[from] anyhow::Error),
}

impl From<reqwest::Error> for Error {
	fn from(value: reqwest::Error) -> Self {
		InternalError::ReqwestError(value).into()
	}
}

impl From<PoolError> for Error {
	fn from(value: PoolError) -> Self { InternalError::PoolError(value).into() }
}

impl From<RunError<RedisError>> for Error {
	fn from(value: RunError<RedisError>) -> Self {
		InternalError::Bb8RedisError(value).into()
	}
}

impl From<RedisError> for Error {
	fn from(value: RedisError) -> Self {
		InternalError::CacheError(value).into()
	}
}

impl From<oauth2::url::ParseError> for Error {
	fn from(value: oauth2::url::ParseError) -> Self {
		InternalError::UrlParseError(value).into()
	}
}

impl From<serde_json::Error> for Error {
	fn from(value: serde_json::Error) -> Self {
		InternalError::SerdeJsonError(value).into()
	}
}

/// Map of constraint names to column names.
static CONSTRAINT_TO_COLUMN: LazyLock<HashMap<&str, &str>> =
	LazyLock::new(|| {
		HashMap::from([
			("pending_profile_email_key", "email"),
			("pending_profile_confirmation_code_key", "confirmation_code"),
			("verified_profile_email_key", "email"),
			("config_verified_role_key", "verified_role"),
			("config_admin_role_key", "admin_role"),
			("config_logging_channel_key", "logging_channel"),
			(
				"config_verification_logging_channel_key",
				"verification_logging_channel",
			),
			(
				"config_confession_approval_channel_key",
				"confession_approval_channel",
			),
			("config_confession_channel_key", "confession_channel"),
		])
	});

impl From<diesel::result::Error> for Error {
	fn from(err: diesel::result::Error) -> Self {
		match &err {
			// No rows returned by query that expected at least one
			diesel::result::Error::NotFound => {
				Self::NotFound("no context provided".to_string())
			},
			// Unique constraint violation
			diesel::result::Error::DatabaseError(
				DatabaseErrorKind::UniqueViolation,
				info,
			) => {
				let constraint_name = info.constraint_name().unwrap();

				match CONSTRAINT_TO_COLUMN.get(constraint_name) {
					Some(field) => {
						Self::Duplicate(format!("{field} is already in use"))
					},
					None => InternalError::DatabaseError(err).into(),
				}
			},
			// Foreign key constraint violation
			diesel::result::Error::DatabaseError(
				DatabaseErrorKind::ForeignKeyViolation,
				info,
			) => Error::ValidationError(info.message().to_string()),
			_ => InternalError::DatabaseError(err).into(),
		}
	}
}
