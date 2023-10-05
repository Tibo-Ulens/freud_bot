insert into profile_statistics
	(profile_discord_id, config_guild_id)
select
	profile.discord_id, config.guild_id
from
	profile, config
on conflict do nothing;
