import logging

from discord import Message

from bot.bot import Bot
from bot.extensions import ErrorHandledCog


logger = logging.getLogger("bot")


GIF_REACTIONS = {
    "kimmoli-gif-25370538": "🔥",
}


class React(ErrorHandledCog):
    @ErrorHandledCog.listener("on_message")
    async def react_to_fire_gif(self, msg: Message):
        if msg.author.bot:
            return

        for gif_url, emoji in GIF_REACTIONS.items():
            if gif_url in msg.content:
                await msg.add_reaction(emoji)


async def setup(bot: Bot):
    await bot.add_cog(React(bot))
