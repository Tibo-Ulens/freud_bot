use axum::Json;
use axum::response::IntoResponse;

mod discord;
mod oauth;
mod verify;

pub use discord::*;
pub use oauth::*;
pub use verify::*;

#[instrument]
#[allow(unused_braces)]
pub async fn me(user: DiscordUser) -> impl IntoResponse { Json(user) }
