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
	Role,
	Route,
};
use tokio::join;

use crate::error::Error;
use crate::extractors::discord::DiscordUser;
use crate::models::database::Config;
use crate::{DbPool, DiscordToken};

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleGuild {
	id:       String,
	name:     String,
	icon_url: Option<String>,
}

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
		.map(|g| {
			let icon_url = match g.icon {
				Some(h) => Some(format!("https://cdn.discordapp.com/icons/{}/{}.webp", g.id, h)),
				None => None,
			};

			SimpleGuild { id: g.id.to_string(), name: g.name, icon_url }
		})
		.collect::<Vec<_>>();

	Ok((StatusCode::OK, Json(manageable_guilds)))
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleGuildInfo {
	id:       String,
	name:     String,
	icon_url: Option<String>,
	channels: Vec<SimpleChannel>,
	roles:    Vec<SimpleRole>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleChannel {
	id:   String,
	name: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct SimpleRole {
	id:    String,
	name:  String,
	color: String,
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
	let roles_request =
		Request::new(Route::GuildRoles { guild_id: guild_id.into() }, LightMethod::Get);

	let (guild, channels, roles) = join!(
		http.fire::<GuildPreview>(guild_request),
		http.fire::<Vec<GuildChannel>>(channels_request),
		http.fire::<Vec<Role>>(roles_request),
	);

	let guild = guild?;

	let channels = channels?
		.into_iter()
		.filter(|c| c.kind == ChannelType::Text)
		.map(|c| SimpleChannel { id: c.id.to_string(), name: c.name })
		.collect();

	let roles = roles?
		.into_iter()
		.map(|r| SimpleRole { id: r.id.to_string(), name: r.name, color: r.colour.hex() })
		.collect();

	let icon_url = match guild.icon {
		Some(h) => Some(format!("https://cdn.discordapp.com/icons/{}/{}.webp", guild.id, h)),
		None => None,
	};

	let guild =
		SimpleGuildInfo { id: guild.id.to_string(), name: guild.name, icon_url, channels, roles };

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
	pub guild_id: String,

	pub verified_role:                Option<String>,
	pub admin_role:                   Option<String>,
	pub logging_channel:              Option<String>,
	pub verification_logging_channel: Option<String>,
	pub confession_approval_channel:  Option<String>,
	pub confession_channel:           Option<String>,

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
