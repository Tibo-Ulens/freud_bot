import asyncio
import logging

import bot
from bot.bot import Bot
from bot.constants import DISCORD_TOKEN


logger = logging.getLogger("main")


async def main():
    logger.info("Creating bot...")
    bot.instance = Bot.create()

    logger.info("Loading extensions...")
    bot.instance.load_extensions()

    logger.info("Starting bot...")
    await bot.instance.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:
        logger.fatal("Fatal startup error")
        logger.fatal(err)

        exit(69)
