from discord import Message, RawReactionActionEvent

from models.config import Config

from bot.bot import Bot
from bot.extensions import ErrorHandledCog


class ReactionPin(ErrorHandledCog):
    @ErrorHandledCog.listener("on_raw_reaction_add")
    async def pin_message_if_needed(self, payload: RawReactionActionEvent):
        if payload.member and payload.member.bot:
            return

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
