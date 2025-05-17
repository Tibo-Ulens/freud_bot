from discord import app_commands, Interaction, Member, Embed

from models.profile import Profile

from bot.bot import Bot
from bot.decorators import check_user_has_admin_role
from bot.extensions import ErrorHandledCog


class Utilities(ErrorHandledCog):
    @app_commands.command(name="info", description="Get information about a user")
    @app_commands.describe(user="The user you wish to spy on")
    @app_commands.guild_only()
    @check_user_has_admin_role()
    async def get_user_info(self, ia: Interaction, user: Member):
        profile = await Profile.find_by_discord_id(user.id)
        if not profile:
            return await ia.response.send_message(
                f"No info for {user.mention} was found", ephemeral=True
            )

        info_embed = Embed(title=f"{user.display_name} info").add_field(
            name="Email", value=f"{profile.email}"
        )
        await ia.response.send_message(embed=info_embed, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Utilities(bot))
