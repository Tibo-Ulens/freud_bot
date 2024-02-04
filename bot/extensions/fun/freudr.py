from discord import Member, app_commands, Interaction, Embed

from bot.bot import Bot
from bot.decorators import check_user_is_verified
from bot.extensions import ErrorHandledCog
from models.profile import Profile


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
        crush_profile = await Profile.find_by_discord_id(crush.id)

        if not crush_profile or not crush_profile.is_verified():
            return await ia.response.send_message(
                f"{crush.mention} is not verified, freudr commands only work on verified members",
                ephemeral=True,
            )

        profile = await Profile.find_by_discord_id(ia.user.id)

        if crush.id in profile.crushes:
            return await ia.response.send_message(
                f"{crush.mention} is already in your list of crushes. If you like them this much, maybe you should send them a DM yourself.",
                ephemeral=True,
            )

        profile.crushes.append(crush.id)
        await profile.save()

        await ia.response.send_message(
            f"Added {crush.mention} to your list of crushes", ephemeral=True
        )

        if ia.user.id in crush_profile.crushes:
            await ia.channel.send(
                f"{ia.user.mention} and {crush.mention} want to get married\nTODO: make this send a DM instead"
            )

    @freudr_group.command(
        name="unlike", description="Remove someone from your list of crushes"
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def unlike(self, ia: Interaction, crush: Member):
        crush_profile = await Profile.find_by_discord_id(crush.id)

        if not crush_profile or not crush_profile.is_verified():
            return await ia.response.send_message(
                f"{crush.mention} is not verified, freudr commands only work on verified members",
                ephemeral=True,
            )

        profile = await Profile.find_by_discord_id(ia.user.id)

        if crush.id not in profile.crushes:
            return await ia.response.send_message(
                f"I get that you don't like {crush.mention}, but they're not even in your list of crushes to begin with.",
                ephemeral=True,
            )

        profile.crushes.remove(crush.id)
        await profile.save()

        await ia.response.send_message(
            f"Removed {crush.mention} from your list of crushes", ephemeral=True
        )

    @freudr_group.command(
        name="list",
        description="See your list of crushes (only you will be able to see it)",
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def show_list(self, ia: Interaction):
        profile = await Profile.find_by_discord_id(ia.user.id)

        if not profile.crushes:
            return await ia.response.send_message(
                "You don't have any crushes, use '/freudr like <user>' to get started",
                ephemeral=True,
            )

        crushes = [f"- <@{crush_id}>" for crush_id in profile.crushes]

        list_embed = Embed(title="Your Crushes", description="\n".join(crushes))

        await ia.response.send_message(embed=list_embed, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Freudr(bot))
