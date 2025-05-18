//! Types and impls related to error handling

use std::collections::HashMap;
use std::sync::LazyLock;

use axum::Json;
use axum::response::{IntoResponse, Response};
use deadpool_lapin::PoolError as QPoolError;
use deadpool_lapin::lapin::Error as LapinError;
use deadpool_redis::PoolError as CPoolError;
use deadpool_redis::redis::RedisError;
use diesel::result::DatabaseErrorKind;
use diesel_async::pooled_connection::deadpool::PoolError as DPoolError;
use http::StatusCode;
use serde_json::json;
use thiserror::Error;
use tokio::sync::mpsc;

/// Top level error type
#[derive(Debug, Error)]
pub enum Error {
	#[error(transparent)]
	AuthorizationError(#[from] AuthorizationError),

	#[error("Duplicate -- {0}")]
	Duplicate(String),

	#[error("Internal Server Error")]
	InternalError,

	#[error("Invalid Confirmation Code")]
	InvalidConfirmationCode,

	#[error("Not Found")]
	NotFound,

	#[error("Invalid -- {0}")]
	ValidationError(String),
}

impl Error {
	#[allow(clippy::enum_glob_use)]
	fn code(&self) -> u32 {
		use AuthorizationError::*;

		match self {
			Self::AuthorizationError(MissingPKCEVerifierCookie) => 0,
			Self::AuthorizationError(MissingCSRFTokenCookie) => 1,
			Self::AuthorizationError(IncorrectCSRFToken) => 2,
			Self::AuthorizationError(MissingAccessTokenCookie) => 3,
			Self::AuthorizationError(MissingRefreshTokenCookie) => 4,
			Self::AuthorizationError(RequestTokenError(_)) => 5,
			Self::Duplicate(_) => 6,
			Self::InternalError => 7,
			Self::NotFound => 8,
			Self::ValidationError(_) => 9,
			Self::InvalidConfirmationCode => 10,
		}
	}

	fn info(&self) -> Option<&str> {
		match self {
			Self::Duplicate(d) => Some(d),
			Self::ValidationError(v) => Some(v),
			Self::AuthorizationError(_)
			| Self::InternalError
			| Self::NotFound
			| Self::InvalidConfirmationCode => None,
		}
	}
}

/// Details about internal errors should not be show to end users, so log a
/// warning and then generate an opaque type
impl From<InternalError> for Error {
	fn from(e: InternalError) -> Self {
		error!("INTERNAL ERROR -- {e}");

		Self::InternalError
	}
}

impl IntoResponse for Error {
	fn into_response(self) -> Response {
		warn!("response error -- {}", self);

		let data = json!({
			"text": self.to_string(),
			"code": self.code(),
			"info": self.info(),
		});

		let status_code = match self {
			Self::InternalError => StatusCode::INTERNAL_SERVER_ERROR,
			Self::AuthorizationError(_) => StatusCode::UNAUTHORIZED,
			Self::NotFound => StatusCode::NOT_FOUND,
			Self::ValidationError(_) => StatusCode::UNPROCESSABLE_ENTITY,
			Self::Duplicate(_) => StatusCode::CONFLICT,
			Self::InvalidConfirmationCode => StatusCode::BAD_REQUEST,
		};

		(status_code, Json(data)).into_response()
	}
}

#[derive(Debug, Error)]
pub enum AuthorizationError {
	#[error("Missing PKCE verifier cookie")]
	MissingPKCEVerifierCookie,

	#[error("Missing CSRF Token cookie")]
	MissingCSRFTokenCookie,

	#[error("Incorrect CSRF Token")]
	IncorrectCSRFToken,

	#[error("Missing access token cookie")]
	MissingAccessTokenCookie,

	#[error("Missing refresh token cookie")]
	MissingRefreshTokenCookie,

	#[error(transparent)]
	RequestTokenError(#[from] anyhow::Error),
}

#[derive(Debug, Error)]
pub enum InternalError {
	#[error("cache pool error -- {0:?}")]
	CachePoolError(#[from] CPoolError),

	#[error("cache error -- {0:?}")]
	CacheError(#[from] RedisError),

	#[error("database error -- {0:?}")]
	DatabaseError(diesel::result::Error),

	#[error("database pool error -- {0:?}")]
	DatabasePoolError(#[from] DPoolError),

	/// Malformed email
	#[error("invalid email -- {0:?}")]
	InvalidEmail(lettre::address::AddressError),

	/// Mailer stopped unexpectedly
	#[error("mailer stopped -- {0:?}")]
	MailerStopped(mpsc::error::SendError<lettre::Message>),

	/// Mail queue is full
	#[error("mail queue full -- {0:?}")]
	MailQueueFull(mpsc::error::TrySendError<lettre::Message>),

	#[error("mail error -- {0:?}")]
	MailError(lettre::error::Error),

	#[error("queue pool error -- {0:?}")]
	QueuePoolError(#[from] QPoolError),

	#[error("queue error -- {0:?}")]
	QueueError(#[from] LapinError),

	#[error("reqwest error -- {0:?}")]
	ReqwestError(#[from] reqwest::Error),

	#[error("JSON (de)serialization error -- {0:?}")]
	SerdeJsonError(#[from] serde_json::Error),

	#[error("Serenity Discord API error -- {0:?}")]
	SerenityError(#[from] serenity::Error),

	#[error("url parsing error -- {0:?}")]
	UrlParseError(#[from] oauth2::url::ParseError),
}

impl From<reqwest::Error> for Error {
	fn from(value: reqwest::Error) -> Self { InternalError::ReqwestError(value).into() }
}

impl From<DPoolError> for Error {
	fn from(value: DPoolError) -> Self { InternalError::DatabasePoolError(value).into() }
}

impl From<CPoolError> for Error {
	fn from(value: CPoolError) -> Self { InternalError::CachePoolError(value).into() }
}

impl From<QPoolError> for Error {
	fn from(value: QPoolError) -> Self { InternalError::QueuePoolError(value).into() }
}

impl From<LapinError> for Error {
	fn from(value: LapinError) -> Self { InternalError::QueueError(value).into() }
}

impl From<RedisError> for Error {
	fn from(value: RedisError) -> Self { InternalError::CacheError(value).into() }
}

impl From<oauth2::url::ParseError> for Error {
	fn from(value: oauth2::url::ParseError) -> Self { InternalError::UrlParseError(value).into() }
}

impl From<serde_json::Error> for Error {
	fn from(value: serde_json::Error) -> Self { InternalError::SerdeJsonError(value).into() }
}

impl From<serenity::Error> for Error {
	fn from(value: serenity::Error) -> Self { InternalError::SerenityError(value).into() }
}

/// Map of constraint names to column names.
static CONSTRAINT_TO_COLUMN: LazyLock<HashMap<&str, &str>> = LazyLock::new(|| {
	HashMap::from([
		("pending_profile_email_key", "email"),
		("pending_profile_confirmation_code_key", "confirmation_code"),
		("verified_profile_email_key", "email"),
		("config_verified_role_key", "verified_role"),
		("config_admin_role_key", "admin_role"),
		("config_logging_channel_key", "logging_channel"),
		("config_verification_logging_channel_key", "verification_logging_channel"),
		("config_confession_approval_channel_key", "confession_approval_channel"),
		("config_confession_channel_key", "confession_channel"),
	])
});

impl From<diesel::result::Error> for Error {
	fn from(err: diesel::result::Error) -> Self {
		match &err {
			// No rows returned by query that expected at least one
			diesel::result::Error::NotFound => Self::NotFound,
			// Unique constraint violation
			diesel::result::Error::DatabaseError(DatabaseErrorKind::UniqueViolation, info) => {
				let constraint_name = info.constraint_name().unwrap();

				match CONSTRAINT_TO_COLUMN.get(constraint_name) {
					Some(field) => Self::Duplicate((*field).to_string()),
					None => InternalError::DatabaseError(err).into(),
				}
			},
			// Foreign key constraint violation
			diesel::result::Error::DatabaseError(DatabaseErrorKind::ForeignKeyViolation, info) => {
				Error::ValidationError(info.message().to_string())
			},
			_ => InternalError::DatabaseError(err).into(),
		}
	}
}

impl From<lettre::address::AddressError> for Error {
	fn from(err: lettre::address::AddressError) -> Self { InternalError::InvalidEmail(err).into() }
}

impl From<mpsc::error::SendError<lettre::Message>> for Error {
	fn from(err: mpsc::error::SendError<lettre::Message>) -> Self {
		InternalError::MailerStopped(err).into()
	}
}

impl From<mpsc::error::TrySendError<lettre::Message>> for Error {
	fn from(err: mpsc::error::TrySendError<lettre::Message>) -> Self {
		InternalError::MailQueueFull(err).into()
	}
}

impl From<lettre::error::Error> for Error {
	fn from(err: lettre::error::Error) -> Self { InternalError::MailError(err).into() }
}
