mod oauth;

use axum::response::IntoResponse;
pub use oauth::*;

#[instrument]
pub async fn me() -> impl IntoResponse { "me" }
