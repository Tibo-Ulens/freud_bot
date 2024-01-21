import random
from enum import Enum
import logging

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
from redis.asyncio import Redis

from models.config import Config
from models.profile_statistics import ProfileStatistics

from bot.bot import Bot
from bot.decorators import (
    check_has_config_option,
    check_user_is_verified,
)
from bot.extensions import ErrorHandledCog


logger = logging.getLogger("bot")


class ConfessionType(Enum):
    NORMAL = (None, "🥷 Anonymous Confession 🥷", "Confession sent")
    RUSSIAN = (
        1 / 6,
        "🔫 Russian Roulette Confession 🔫",
        "Russian roulette confession sent",
    )
    EXTREME = (
        1 / 2,
        "💥 Extreme Roulette Confession 💥",
        "Extreme roulette confession sent",
    )

    @property
    def chance(self):
        return self.value[0]

    @property
    def title(self):
        return self.value[1]

    @property
    def success_msg(self):
        return self.value[2]


class Confession:
    def __init__(
        self,
        confession: str,
        poster: Member,
        type_: ConfessionType,
        reply: str | None,
        redis: Redis,
        confession_channel: TextChannel,
        approval_channel: TextChannel,
    ):
        self.confession = confession
        self.poster = poster
        self.type_ = type_
        self.reply = reply
        self.redis = redis
        self.confession_channel = confession_channel
        self.approval_channel = approval_channel

    async def send_pending(self):
        pending_embed = Embed(
            colour=Colour.from_rgb(255, 255, 0),
            title=self.type_.title,
            description=self.confession,
        )

        if self.reply is not None:
            pending_embed.set_author(name=f"Reply to #{self.reply}")

        pending_view = PendingApprovalView(
            redis=self.redis,
            confession=pending_embed,
            reply=self.reply,
            confession_channel=self.confession_channel,
            poster=self.poster,
            chance=self.type_.chance,
        )

        pending_view.message = await self.approval_channel.send(
            embed=pending_embed,
            view=pending_view,
        )


class PendingApprovalView(View):
    def __init__(
        self,
        redis: Redis,
        confession: Embed,
        reply: str | None,
        confession_channel: TextChannel,
        poster: Member,
        chance: float | None,
    ):
        super().__init__(timeout=None)
        self.redis = redis
        self.confession = confession
        self.reply = reply
        self.confession_channel = confession_channel
        self.poster = poster
        self.chance = chance

    @discord.ui.button(label="✓", style=ButtonStyle.green)
    async def approve(self, ia: Interaction, _btn: Button):
        for item in self.children:
            item.disabled = True

        confession_id = await self.redis.incr("confessionid")

        self.confession.colour = Colour.from_str("#3fc03f")
        self.confession.title = f"{self.confession.title} (#{confession_id})"

        await self.message.edit(embed=self.confession, view=self)
        await ia.response.defer()

        actual_confession = self.confession.copy()

        actual_confession.colour = Colour.random()

        if self.chance is not None and random.random() <= self.chance:
            await ProfileStatistics.increment_exposed_count(self.poster.id, ia.guild_id)

            actual_confession.add_field(name="Sent By", value=self.poster.mention)

        if self.reply is not None:
            reply_msg_id = int(await self.redis.get(f"confession:{self.reply}"))
            reply_msg = self.confession_channel.get_partial_message(reply_msg_id)

            try:
                thread = await reply_msg.create_thread(
                    name="confession", reason="confession reply"
                )
            except discord.errors.HTTPException as err:
                if err.code == 160004:
                    thread = self.confession_channel.get_thread(reply_msg_id)
                else:
                    raise err

            actual_msg = await thread.send(embed=actual_confession)
        else:
            actual_msg = await self.confession_channel.send(embed=actual_confession)

        await self.redis.set(f"confession:{confession_id}", actual_msg.id)
        await self.redis.expire(f"confession:{confession_id}", 86400)

    @discord.ui.button(label="⨯", style=ButtonStyle.red)
    async def reject(self, ia: Interaction, _btn: Button):
        for item in self.children:
            item.disabled = True

        self.confession.colour = Colour.from_str("#fb4934")

        await self.message.edit(embed=self.confession, view=self)
        await ia.response.defer()


class Confess(ErrorHandledCog):
    confess_group = app_commands.Group(
        name="confess", description="Confession related commands", guild_only=True
    )

    async def confess_inner(
        self,
        ia: Interaction,
        confession: str,
        type_: ConfessionType,
        reply: str | None = None,
    ):
        config = await Config.get(ia.guild_id)
        approval_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_approval_channel
        )
        confession_channel = discord.utils.get(
            ia.guild.channels, id=config.confession_channel
        )

        if reply is not None:
            reply_msg_id = await self.bot.redis.get(f"confession:{reply}")
            if reply_msg_id is None:
                await ia.response.send_message(
                    f"{reply} is not a valid confession ID", ephemeral=True
                )
                return

            try:
                await confession_channel.fetch_message(int(reply_msg_id))
            except discord.errors.HTTPException:
                await ia.response.send_message(
                    f"{reply} is not a valid confession ID (keep in mind that you cannot reply to other replies)",
                    ephemeral=True,
                )
                return

        confession_wrapper = Confession(
            confession=confession,
            poster=ia.user,
            type_=type_,
            reply=reply,
            redis=self.bot.redis,
            confession_channel=confession_channel,
            approval_channel=approval_channel,
        )

        await confession_wrapper.send_pending()

        await ia.response.send_message(
            content=confession_wrapper.type_.success_msg, ephemeral=True
        )

    @confess_group.command(
        name="normal", description="send a normal, anonymous confession"
    )
    @app_commands.describe(
        confession="The confession you want to post",
        reply="The ID of the confession you want to reply to",
    )
    @check_has_config_option("confession_approval_channel")
    @check_has_config_option("confession_channel")
    @check_user_is_verified()
    async def normal_confess(
        self, ia: Interaction, confession: str, reply: str | None = None
    ):
        await self.confess_inner(ia, confession, ConfessionType.NORMAL, reply)

    @confess_group.command(
        name="russian",
        description="send a russian roulette confession with a 1 in 6 chance of not being anonymous",
    )
    @app_commands.describe(
        confession="The confession you want to post",
        reply="The ID of the confession you want to reply to",
    )
    @check_has_config_option("confession_approval_channel")
    @check_has_config_option("confession_channel")
    @check_user_is_verified()
    async def russian_confess(
        self, ia: Interaction, confession: str, reply: str | None = None
    ):
        await self.confess_inner(ia, confession, ConfessionType.RUSSIAN, reply)

    @confess_group.command(
        name="extreme",
        description="send an extreme roulette confession with a 1 in 2 chance of not being anonymous",
    )
    @app_commands.describe(
        confession="The confession you want to post",
        reply="The ID of the confession you want to reply to",
    )
    @check_has_config_option("confession_approval_channel")
    @check_has_config_option("confession_channel")
    @check_user_is_verified()
    async def russian_confess(
        self, ia: Interaction, confession: str, reply: str | None = None
    ):
        await self.confess_inner(ia, confession, ConfessionType.EXTREME, reply)


async def setup(bot: Bot):
    await bot.add_cog(Confess(bot))
