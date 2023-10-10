import asyncio
from datetime import datetime, timezone, timedelta
from bot.bot import Bot
from bot.tasks import task_logger

from models.profile_statistics import ProfileStatistics


async def freudpoint_increment():
    while True:
        now = datetime.now().astimezone(timezone.utc).replace(microsecond=0)
        next_midnight = (
            (now + timedelta(days=1))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .astimezone(timezone.utc)
        )

        delay = (next_midnight - now).total_seconds()

        task_logger.info(f"waiting {delay}s until next midnight")
        await asyncio.sleep(delay)

        task_logger.info("incrementing spendable freudpoints...")
        await ProfileStatistics.increment_spendable_freudpoints()
        task_logger.info("done")


async def setup(bot: Bot):
    bot.loop.create_task(freudpoint_increment())
