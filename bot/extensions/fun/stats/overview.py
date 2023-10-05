from discord import (
    app_commands,
    Interaction,
    Member,
    Embed,
)

from models.profile import Profile

from bot.bot import Bot
from bot.decorators import (
    check_user_is_verified,
)
from bot.extensions import ErrorHandledCog


class FreudStatOverview(ErrorHandledCog):
    freudstat_group = app_commands.Group(
        name="freudstat", description="FreudStats personal and global statistics"
    )

    @freudstat_group.command(
        name="profile",
        description="Get an overview of your personal FreudStats profile",
    )
    @app_commands.guild_only()
    @check_user_is_verified()
    async def show_profile(self, ia: Interaction):
        user = await Profile.find_by_discord_id(ia.user.id)

        profile_embed = (
            Embed(title=f"{ia.user.display_name}s Profile", colour=ia.user.colour)
            .set_thumbnail(url=ia.user.display_avatar.url)
            .add_field(name="FreudPoints", value=user.freudpoints, inline=True)
            .add_field(
                name="Spendable FreudPoints",
                value=user.spendable_freudpoints,
                inline=True,
            )
        )

        return await ia.response.send_message(embed=profile_embed)


async def setup(bot: Bot):
    await bot.add_cog(FreudStatOverview(bot))
