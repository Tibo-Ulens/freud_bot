from typing import Optional

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
from models.profile_statistics import ProfileStatistics


class FreudPoints(ErrorHandledCog):
    freudpoint_group = app_commands.Group(
        name="freudpoint", description="FreudPoint awards and leaderboards"
    )

    @freudpoint_group.command(name="award", description="Award FreudPoints to somebody")
    @app_commands.describe(user="The user to award points to")
    @app_commands.describe(amount="The amount of points to award")
    @app_commands.guild_only()
    @check_user_is_verified()
    async def award_freudpoints(
        self, ia: Interaction, user: Member, amount: Optional[int] = 1
    ):
        awarder_stats = await ProfileStatistics.get(ia.user.id, ia.guild_id)

        if awarder_stats.spendable_freudpoints < amount:
            return await ia.response.send_message(
                "You don't have enough FreudPoints available to give out!\nPlease wait a few days until you have enough",
                ephemeral=True,
            )

        awardee_stats = await ProfileStatistics.get(user.id, ia.guild_id)

        if awardee_stats is None:
            return await ia.response.send_message(
                f"{user.display_name} is not verified and is not elligible for FreudPoints"
            )

        awarder_stats.spendable_freudpoints -= amount
        awardee_stats.freudpoints += amount

        await awarder_stats.save()
        await awardee_stats.save()

        return await ia.response.send_message(
            f"{user.display_name} has been awarded {amount} FreudPoint(s)!",
            ephemeral=True,
        )


async def setup(bot: Bot):
    await bot.add_cog(FreudPoints(bot))
