import logging

from discord import Message, RawReactionActionEvent

from models.config import Config

from bot.bot import Bot
from bot.extensions import ErrorHandledCog


logger = logging.getLogger("bot")


class ReactionPin(ErrorHandledCog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @ErrorHandledCog.listener("on_raw_reaction_add")
    async def pin_message_if_needed(self, payload: RawReactionActionEvent):
        if payload.emoji.name != "📌":
            return

        channel = self.bot.get_channel(payload.channel_id)
        message: Message = await channel.fetch_message(payload.message_id)
        count = len(list(filter(lambda r: r.emoji == "📌", message.reactions)))

        guild_config = await Config.get(message.guild.id)

        if (
            guild_config is not None
            and guild_config.pin_reaction_threshold is not None
            and count == guild_config.pin_reaction_threshold
        ):
            await message.pin()


async def setup(bot: Bot):
    await bot.add_cog(ReactionPin(bot))
