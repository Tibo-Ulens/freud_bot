use axum::Json;
use axum::response::IntoResponse;

mod config;
mod oauth;
mod verify;

pub use config::*;
pub use oauth::*;
pub use verify::*;

use crate::extractors::discord::DiscordUser;

#[instrument]
#[allow(unused_braces)]
pub async fn me(user: DiscordUser) -> impl IntoResponse { Json(user) }
