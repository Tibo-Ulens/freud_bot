import random

import discord
from discord import (
    app_commands,
    Interaction,
    ButtonStyle,
    TextChannel,
    Embed,
    Colour,
    Member,
)
from discord.ui import View, Button

from models.config import Config

from bot import util
from bot.bot import Bot
from bot.decorators import (
    check_has_config_option,
    check_user_is_verified,
)
from bot.extensions import ErrorHandledCog


async def send_pending_confession(
    confession: str,
    confession_channel: TextChannel,
    approval_channel: TextChannel,
    russian_roulette_user: Member = None,
):
    confession_embed = Embed(description=confession, colour=Colour.from_str("#88a8bf"))
    pending_view = PendingApprovalView(
        confession=confession_embed,
        confession_channel=confession_channel,
        russian_roulette_user=russian_roulette_user,
    )

    pending_view.message = await approval_channel.send(
        embed=confession_embed,
        view=pending_view,
    )


class PendingApprovalView(View):
    def __init__(
        self,
        confession: Embed,
        confession_channel: TextChannel,
        russian_roulette_user: Member = None,
    ):
        super().__init__(timeout=None)
        self.confession = confession
        self.confession_channel = confession_channel
        self.russian_roulette_user = russian_roulette_user

    @discord.ui.button(label="✓", style=ButtonStyle.green)
    async def approve(self, ia: Interaction, btn: Button):
        if self.russian_roulette_user is not None and random.random() <= 1 / 6:
            self.confession.description = f"{util.render_user(self.russian_roulette_user)}: {self.confession.description}"

        await self.confession_channel.send(embed=self.confession)

        for item in self.children:
            item.disabled = True

        embed: Embed = self.message.embeds[0]
        embed.colour = Colour.from_str("#3fc03f")

        await self.message.edit(embed=embed, view=self)
        await ia.response.defer()

    @discord.ui.button(label="⨯", style=ButtonStyle.red)
    async def reject(self, ia: Interaction, btn: Button):
        for item in self.children:
            item.disabled = True

        embed: Embed = self.message.embeds[0]
        embed.colour = Colour.from_str("#fb4934")

        await self.message.edit(embed=embed, view=self)
        await ia.response.defer()


class Confess(ErrorHandledCog):
    @app_commands.command(name="confess", description="send an anonymous confession")
    @app_commands.describe(confession="The confession you want to post")
    @app_commands.guild_only()
    @check_has_config_option("confession_approval_channel")
    @check_has_config_option("confession_channel")
    @check_user_is_verified()
    async def confess(self, ia: Interaction, confession: str):
        config = await Config.get(ia.guild_id)
        approval_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_approval_channel
        )
        confession_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_channel
        )

        await send_pending_confession(confession, confession_channel, approval_channel)

        await ia.response.send_message(content="Confession sent", ephemeral=True)

    @app_commands.command(
        name="russianconfess",
        description="send confession with a 1 in 6 chance of not being anonymous",
    )
    @app_commands.describe(confession="The confession you want to post")
    @app_commands.guild_only()
    @check_has_config_option("confession_approval_channel")
    @check_has_config_option("confession_channel")
    @check_user_is_verified()
    async def russian_confess(self, ia: Interaction, confession: str):
        config = await Config.get(ia.guild_id)
        approval_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_approval_channel
        )
        confession_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_channel
        )

        await send_pending_confession(
            confession,
            confession_channel,
            approval_channel,
            russian_roulette_user=ia.user,
        )

        await ia.response.send_message(
            content="Russian roulette confession sent", ephemeral=True
        )


async def setup(bot: Bot):
    await bot.add_cog(Confess(bot))
