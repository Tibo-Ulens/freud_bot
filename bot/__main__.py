import asyncio
import logging
from signal import SIGTERM

import bot
from bot.bot import Bot
from bot.constants import DISCORD_TOKEN


logger = logging.getLogger("main")


async def main():
    logger.info("Creating bot...")
    bot.instance = await Bot.create()

    logger.info("Loading extensions...")
    await bot.instance.load_extensions()

    logger.info("Starting bot...")
    await bot.instance.start(DISCORD_TOKEN)


async def close(task):
    logger.info("Closing bot...")
    await bot.instance.close()
    task.cancel()
    task.exception()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    task = loop.create_task(main())

    loop.add_signal_handler(SIGTERM, lambda: loop.create_task(close(task)))

    try:
        # asyncio.run(main())
        loop.run_until_complete(task)
    except KeyboardInterrupt as interrupt:
        logger.fatal("Received keyboard interrupt")
        loop.run_until_complete(close(task))
        loop.run_forever()
    except Exception as err:
        logger.fatal("Fatal startup error")
        logger.fatal(err)
    finally:
        loop.close()
        exit(69)
