from discord import Member, app_commands, Interaction

from bot.bot import Bot
from bot.decorators import check_user_is_verified
from bot import constants
from bot.extensions import ErrorHandledCog


class Freudr(ErrorHandledCog):
    freudr_group = app_commands.Group(
        name="freudr", description="Freudr dating service commands", guild_only=True
    )

    @freudr_group.command(
        name="like", description="Add someone to your list of crushes"
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def like(self, ia: Interaction, crush: Member):
        pass

    @freudr_group.command(
        name="unlike", description="Remove someone from your list of crushes"
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def unlike(self, ia: Interaction, crush: Member):
        pass

    @freudr_group.command(
        name="list",
        description="See your list of crushes (only you will be able to see it)",
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def show_list(self, ia: Interaction):
        pass


async def setup(bot: Bot):
    await bot.add_cog(Freudr(bot))
