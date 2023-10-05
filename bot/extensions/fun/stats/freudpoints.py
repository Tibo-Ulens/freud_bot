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


class FreudPoints(ErrorHandledCog):
    freudpoint_group = app_commands.Group(
        name="freudpoint", description="FreudPoint awards and leaderboards"
    )

    @freudpoint_group.command(
        name="award", description="Award a single FreudPoint to the given user"
    )
    @app_commands.describe(user="The user to award the point to")
    @app_commands.guild_only()
    @check_user_is_verified()
    async def award_freudpoint(self, ia: Interaction, user: Member):
        awarder = await Profile.find_by_discord_id(ia.user.id)

        if awarder.spendable_freudpoints == 0:
            return await ia.response.send_message(
                "You don't have any FreudPoints available to give out!\nPlease wait 1 day",
                ephemeral=True,
            )

        awardee = await Profile.find_by_discord_id(user.id)

        awarder.spendable_freudpoints -= 1
        awardee.freudpoints += 1

        await awarder.save()
        await awardee.save()

        return await ia.response.send_message(
            f"{user.display_name} has been awarded 1 FreudPoint!", ephemeral=True
        )


async def setup(bot: Bot):
    await bot.add_cog(FreudPoints(bot))
