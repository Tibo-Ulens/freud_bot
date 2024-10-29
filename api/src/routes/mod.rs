use axum::response::IntoResponse;

mod discord;
mod oauth;

use axum::Json;
pub use discord::*;
pub use oauth::*;

#[instrument]
pub async fn me(user: DiscordUser) -> impl IntoResponse { Json(user) }
