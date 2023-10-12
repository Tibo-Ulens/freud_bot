insert into profile_statistics
	(profile_discord_id, config_guild_id)
select
	profile.discord_id, config.guild_id
from
	profile, config
where
	profile.email is not null and profile.confirmation_code is null
on conflict do nothing;
