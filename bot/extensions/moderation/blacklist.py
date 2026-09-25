from discord import app_commands, Embed, Interaction

from models.config import Config
from models.email_blacklist import EmailBlacklist
from models.profile import Profile, normalize_email

from bot.bot import Bot
from bot.decorators import check_user_has_admin_role
from bot.extensions import ErrorHandledCog
from bot.extensions.moderation.verification import EMAIL_REGEX, grant_verified_role


# Leave some room below discords 4096 character embed description limit
MAX_LIST_LENGTH = 4000


class Blacklist(ErrorHandledCog):
    blacklist_group = app_commands.Group(
        name="blacklist",
        description="Manage the emails that can't verify in this server",
        guild_only=True,
    )

    @blacklist_group.command(
        name="add", description="Prevent an email from verifying in this server"
    )
    @app_commands.describe(email="The email to blacklist")
    @check_user_has_admin_role()
    async def add(self, ia: Interaction, email: str):
        await ia.response.defer(ephemeral=True, thinking=True)

        email = normalize_email(email)
        if not EMAIL_REGEX.match(email):
            return await ia.followup.send(f"'{email}' is not a valid UGent email")

        if not await EmailBlacklist.add(ia.guild_id, email):
            return await ia.followup.send(f"'{email}' is already blacklisted")

        log_msg = f"{ia.user.mention} blacklisted '{email}'"

        # Take the verified role away from whoever is using this email here
        guild_config = await Config.get(ia.guild_id)
        profile = await Profile.find_by_email(email)
        member = ia.guild.get_member(profile.discord_id) if profile else None
        if (
            member is not None
            and guild_config.verified_role is not None
            and member.get_role(guild_config.verified_role) is not None
        ):
            await member.remove_roles(ia.guild.get_role(guild_config.verified_role))
            log_msg += f", {member.mention} lost their verified role"

        self.bot.discord_logger.info(log_msg, guild=ia.guild, log_type="verification")

        return await ia.followup.send(f"Blacklisted '{email}'")

    @blacklist_group.command(
        name="remove", description="Allow a blacklisted email to verify again"
    )
    @app_commands.describe(email="The email to remove from the blacklist")
    @check_user_has_admin_role()
    async def remove(self, ia: Interaction, email: str):
        await ia.response.defer(ephemeral=True, thinking=True)

        email = normalize_email(email)
        if not await EmailBlacklist.remove(ia.guild_id, email):
            return await ia.followup.send(f"'{email}' is not blacklisted")

        log_msg = f"{ia.user.mention} removed '{email}' from the blacklist"

        # Give the role back if they're already verified through another server
        profile = await Profile.find_by_email(email)
        member = ia.guild.get_member(profile.discord_id) if profile else None
        if (
            member is not None
            and profile.is_verified()
            and await grant_verified_role(self.bot, ia.guild, member, profile)
        ):
            log_msg += f", {member.mention} got their verified role back"

        self.bot.discord_logger.info(log_msg, guild=ia.guild, log_type="verification")

        return await ia.followup.send(f"Removed '{email}' from the blacklist")

    @blacklist_group.command(
        name="list", description="Show the emails blacklisted in this server"
    )
    @check_user_has_admin_role()
    async def show(self, ia: Interaction):
        await ia.response.defer(ephemeral=True, thinking=True)

        entries = await EmailBlacklist.get_for_guild(ia.guild_id)
        if len(entries) == 0:
            return await ia.followup.send("The blacklist is empty")

        lines: list[str] = []
        length = 0
        for entry in entries:
            line = f"`{entry.email}`"
            if entry.banned_discord_id is not None:
                line += f" (banned <@{entry.banned_discord_id}>)"

            length += len(line) + 1
            if length > MAX_LIST_LENGTH:
                lines.append(f"... and {len(entries) - len(lines)} more")
                break

            lines.append(line)

        embed = Embed(
            title=f"Blacklisted emails ({len(entries)})", description="\n".join(lines)
        )

        return await ia.followup.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Blacklist(bot))
