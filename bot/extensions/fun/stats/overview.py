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
from models.profile_statistics import ProfileStatistics


class FreudStatOverview(ErrorHandledCog):
    freudstat_group = app_commands.Group(
        name="freudstat", description="FreudStats personal and global statistics"
    )

    @freudstat_group.command(
        name="me",
        description="Get an overview of your personal FreudStats profile",
    )
    @app_commands.guild_only()
    @check_user_is_verified()
    async def show_me(self, ia: Interaction):
        user = await Profile.find_by_discord_id(ia.user.id)
        stats = await ProfileStatistics.get(ia.user.id, ia.guild_id)

        rank = await user.get_freudpoint_rank()

        profile_embed = (
            Embed(title=f"{ia.user.display_name}s Profile", colour=ia.user.colour)
            .set_thumbnail(url=ia.user.display_avatar.url)
            .add_field(
                name="FreudPoints",
                value=f"#{rank + 1} ({stats.freudpoints} FP)",
                inline=True,
            )
            .add_field(
                name="Spendable FreudPoints",
                value=stats.spendable_freudpoints,
                inline=True,
            )
        )

        return await ia.response.send_message(embed=profile_embed)

    @freudstat_group.command(
        name="profile", description="Get an overview of somebodies profile"
    )
    @app_commands.describe(user="The user whose profile you want to see")
    @app_commands.guild_only()
    @check_user_is_verified()
    async def show_profile(self, ia: Interaction, user: Member):
        db_user = await Profile.find_by_discord_id(user.id)

        if db_user is None:
            return await ia.response.send_message(
                f"{user.display_name} is not verified and doesn't have a profile"
            )

        stats = await ProfileStatistics.get(user.id, ia.guild_id)
        rank = await db_user.get_freudpoint_rank()

        profile_embed = (
            Embed(title=f"{user.display_name}s Profile", colour=user.colour)
            .set_thumbnail(url=user.display_avatar.url)
            .add_field(
                name="FreudPoints",
                value=f"#{rank + 1} ({stats.freudpoints} FP)",
                inline=True,
            )
        )

        return await ia.response.send_message(embed=profile_embed)

    @freudstat_group.command(
        name="leaderboard",
        description="See a leaderboard of members with the most FreudPoints",
    )
    @app_commands.guild_only()
    @check_user_is_verified()
    async def show_leaderboard(self, ia: Interaction):
        top_10 = await ProfileStatistics.get_freudpoint_top_10(ia.guild_id)

        top_10 = [
            f"#{i + 1} - <@{p.profile_discord_id}> ({p.freudpoints})"
            for i, p in enumerate(top_10)
        ]

        leaderboard = Embed(
            title="Members with the most FreudPoints", description="\n".join(top_10)
        )

        return await ia.response.send_message(embed=leaderboard)


async def setup(bot: Bot):
    await bot.add_cog(FreudStatOverview(bot))
