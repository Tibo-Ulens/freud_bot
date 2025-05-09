use axum::Json;
use axum::response::IntoResponse;

mod oauth;
mod verify;

pub use oauth::*;
pub use verify::*;

use crate::extractors::discord::DiscordUser;

#[instrument]
#[allow(unused_braces)]
pub async fn me(user: DiscordUser) -> impl IntoResponse { Json(user) }
