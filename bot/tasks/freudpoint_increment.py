import asyncio
from datetime import datetime, timezone, timedelta
import logging
from bot.bot import Bot

from models.profile_statistics import ProfileStatistics


logger = logging.getLogger("freudpoint_increment")


async def freudpoint_increment():
    while True:
        now = datetime.now().astimezone(timezone.utc).replace(microsecond=0)
        next_midnight = (
            (now + timedelta(days=1))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .astimezone(timezone.utc)
        )

        delay = (next_midnight - now).total_seconds()

        logger.info(f"waiting {delay}s until next midnight")
        await asyncio.sleep(delay)

        logger.info("incrementing spendable freudpoints...")
        await ProfileStatistics.increment_spendable_freudpoints()
        logger.info("done")


async def setup(bot: Bot):
    bot.loop.create_task(freudpoint_increment())
