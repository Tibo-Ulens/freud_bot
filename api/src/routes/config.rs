use axum::extract::{Path, State};
use axum::response::IntoResponse;
use axum::{Extension, Json};
use http::StatusCode;
use oauth2::AccessToken;
use serde::{Deserialize, Serialize};
use serenity::all::{
	ChannelType,
	GuildChannel,
	GuildInfo,
	GuildPreview,
	Http,
	LightMethod,
	Permissions,
	Request,
	Route,
};
use tokio::join;

use crate::error::Error;
use crate::extractors::discord::DiscordUser;
use crate::models::database::Config;
use crate::{DbPool, DiscordToken};

#[instrument(skip(pool, token))]
pub async fn get_manageable_guilds(
	State(pool): State<DbPool>,
	Extension(token): Extension<AccessToken>,
	user: DiscordUser,
) -> Result<impl IntoResponse, Error> {
	let mut conn = pool.get().await?;

	let http = Http::new(&format!("Bearer {}", token.secret()));
	let request = Request::new(Route::UserMeGuilds, LightMethod::Get);

	let (user_guilds, configs) =
		join!(http.fire::<Vec<GuildInfo>>(request), Config::all(&mut conn));

	let config_ids = configs?.iter().map(|c| c.guild_id.0).collect::<Vec<_>>();

	let manageable_guilds = user_guilds?
		.into_iter()
		.filter(|g| {
			g.permissions.contains(Permissions::ADMINISTRATOR | Permissions::MANAGE_GUILD)
				&& config_ids.contains(&g.id.into())
		})
		.collect::<Vec<_>>();

	Ok((StatusCode::OK, Json(manageable_guilds)))
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleGuild {
	id:       u64,
	name:     String,
	icon_url: Option<String>,
	channels: Vec<SimpleChannel>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleChannel {
	id:   u64,
	name: String,
}

#[instrument(skip(token))]
pub async fn get_guild_info(
	State(token): State<DiscordToken>,
	Path(guild_id): Path<u64>,
	user: DiscordUser,
) -> Result<impl IntoResponse, Error> {
	// Have to use a bot token here because apparently users have no need for
	// guild information
	//
	// discord devs if i ever get my hands on you istfg
	let http = Http::new(&format!("Bot {}", token.0));

	let guild_request =
		Request::new(Route::GuildPreview { guild_id: guild_id.into() }, LightMethod::Get);
	let channels_request =
		Request::new(Route::GuildChannels { guild_id: guild_id.into() }, LightMethod::Get);

	let (guild, channels) = join!(
		http.fire::<GuildPreview>(guild_request),
		http.fire::<Vec<GuildChannel>>(channels_request),
	);

	let guild = guild?;

	let channels = channels?
		.into_iter()
		.filter(|c| c.kind == ChannelType::Text)
		.map(|c| SimpleChannel { id: c.id.into(), name: c.name })
		.collect();

	let icon_url = match guild.icon {
		Some(h) => Some(format!("https://cdn.discordapp.com/icons/{}/{}.webp", guild.id, h)),
		None => None,
	};

	let guild = SimpleGuild { id: guild.id.into(), name: guild.name, icon_url, channels };

	Ok((StatusCode::OK, Json(guild)))
}

#[instrument(skip(token))]
pub async fn get_guild_channels(
	Extension(token): Extension<AccessToken>,
	Path(guild_id): Path<u64>,
	user: DiscordUser,
) -> Result<impl IntoResponse, Error> {
	let http = Http::new(&format!("Bearer {}", token.secret()));
	let request =
		Request::new(Route::GuildChannels { guild_id: guild_id.into() }, LightMethod::Get);
	let guild_channels = http.fire::<Vec<GuildChannel>>(request).await?;

	Ok((StatusCode::OK, Json(guild_channels)))
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct PatchConfigData {
	pub guild_id: u64,

	pub verified_role:                Option<u64>,
	pub admin_role:                   Option<u64>,
	pub logging_channel:              Option<u64>,
	pub verification_logging_channel: Option<u64>,
	pub confession_approval_channel:  Option<u64>,
	pub confession_channel:           Option<u64>,

	pub pin_reaction_threshold: Option<i32>,

	pub request_verification_message: Option<String>,
}

// #[instrument(skip(token))]
// pub async fn patch_config(
// 	Extension(token): Extension<AccessToken>,
// 	user: DiscordUser,
// 	Json(data): Json<PatchConfigData>
// ) -> Result<impl IntoResponse, Error> {
// 	let http = Http::new(&format!("Bearer {}", token.secret()));

// 	Ok(NoContent)
// }
