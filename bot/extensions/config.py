from discord.ext import commands
from discord.ext.commands import Cog, command, Context
import logging

from bot.bot import Bot
from bot import constants


logger = logging.getLogger("bot")


class Config(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(name="freud_sync")
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context):
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)

        logger.info(f"synced {len(synced)} commands to {ctx.guild.name}")
        await ctx.reply(f"synced {len(synced)} commands to the current guild")


async def setup(bot: Bot):
    await bot.add_cog(Config(bot))
