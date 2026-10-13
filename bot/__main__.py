import asyncio
import logging
from signal import SIGTERM
import sys
import time

import bot
from bot.bot import Bot
from bot.constants import DISCORD_TOKEN


logger = logging.getLogger("main")


# Docker restarts the bot within a minute after it exits, and Discord resets
# the token of a bot that logs in more than 1000 times a day. Waiting this
# long after a fatal error keeps a restart loop well below that
FATAL_ERROR_DELAY = 600


async def main():
    logger.info("Creating bot...")
    bot.instance = await Bot.create(DISCORD_TOKEN)

    logger.info("Loading extensions...")
    await bot.instance.load_extensions()

    logger.info("Starting tasks...")
    await bot.instance.start_tasks()

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

        # Let SIGTERM stop the bot right away instead of being swallowed
        loop.remove_signal_handler(SIGTERM)

        logger.fatal(f"waiting {FATAL_ERROR_DELAY}s before exiting")
        time.sleep(FATAL_ERROR_DELAY)
    finally:
        loop.close()
        sys.exit(69)
