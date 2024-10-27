//! Types and impls related to error handling

use axum::response::{IntoResponse, Response};
use bb8::RunError;
use http::{header, StatusCode};
use redis::RedisError;
use thiserror::Error;

/// Top level error type
#[derive(Debug, Error)]
pub enum Error {
	#[error("Internal Server Error")]
	InternalError,

	#[error(transparent)]
	AuthorizationError(#[from] AuthorizationError),
}

/// Details about internal errors should not be show to end users, so log an
/// error and then generate an opaque type
impl From<InternalError> for Error {
	fn from(err: InternalError) -> Self {
		error!("internal error -- {}", err);

		Self::InternalError
	}
}

impl IntoResponse for Error {
	fn into_response(self) -> Response {
		error!("{}", self);

		let body = self.to_string();

		let status_code = match self {
			Self::InternalError => StatusCode::INTERNAL_SERVER_ERROR,
			Self::AuthorizationError(_) => StatusCode::FORBIDDEN,
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
	#[error(transparent)]
	ReqwestError(#[from] reqwest::Error),

	#[error(transparent)]
	Bb8RedisError(#[from] RunError<RedisError>),

	#[error(transparent)]
	CacheError(#[from] RedisError),

	#[error(transparent)]
	UrlParseError(#[from] oauth2::url::ParseError),
}

impl From<reqwest::Error> for Error {
	fn from(value: reqwest::Error) -> Self { InternalError::ReqwestError(value).into() }
}

impl From<RunError<RedisError>> for Error {
	fn from(value: RunError<RedisError>) -> Self { InternalError::Bb8RedisError(value).into() }
}

impl From<RedisError> for Error {
	fn from(value: RedisError) -> Self { InternalError::CacheError(value).into() }
}

impl From<oauth2::url::ParseError> for Error {
	fn from(value: oauth2::url::ParseError) -> Self { InternalError::UrlParseError(value).into() }
}

#[derive(Debug, Error)]
pub enum AuthorizationError {
	#[error("Missing PKCE verifier cookie")]
	MissingPKCEVerifierCookie,

	#[error(transparent)]
	RequestTokenError(#[from] anyhow::Error),
}
