from discord import (
    app_commands,
    Interaction,
    Member,
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

        return await ia.response.send_message(f"FreudPoints: {user.freudpoints}")


async def setup(bot: Bot):
    await bot.add_cog(FreudStatOverview(bot))
