import asyncio
import time
from discord import Member, app_commands, Interaction, Embed

from bot.bot import Bot
from bot.decorators import check_user_is_verified
from bot.extensions import ErrorHandledCog
from models.profile import Profile
from models.profile_statistics import ProfileStatistics


class Freudr(ErrorHandledCog):
    @staticmethod
    async def ensure_has_statistics(id1: int, id2: int, guild_id: int):
        await asyncio.gather(
            *[
                ProfileStatistics.get(id1, guild_id),
                ProfileStatistics.get(id2, guild_id),
            ]
        )

    @staticmethod
    def hash_match(user_id, crush_id) -> int:
        if user_id <= crush_id:
            return hash(f"{user_id}:{crush_id}")

        return hash(f"{crush_id}:{user_id}")

    async def is_match_cached(self, user_id: int, crush_id: int) -> bool:
        match_hash = self.hash_match(user_id, crush_id)

        timestamp = int(time.time())
        await self.bot.redis.zremrangebyscore("freudr_matches", 0, timestamp - 86400)

        score = await self.bot.redis.zscore("freudr_matches", match_hash)

        return score is not None

    async def cache_match(self, user_id: int, crush_id: int):
        match_hash = self.hash_match(user_id, crush_id)

        timestamp = int(time.time())
        await self.bot.redis.zremrangebyscore("freudr_matches", 0, timestamp - 86400)

        await self.bot.redis.zadd("freudr_matches", {match_hash: timestamp}, nx=True)

    freudr_group = app_commands.Group(
        name="freudr", description="Freudr dating service commands", guild_only=True
    )

    @freudr_group.command(
        name="like", description="Add someone to your list of crushes"
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def like(self, ia: Interaction, crush: Member):
        crush_profile = await Profile.find_by_discord_id(crush.id)

        if not crush_profile or not crush_profile.is_verified():
            return await ia.response.send_message(
                f"{crush.mention} is not verified, freudr commands only work on verified members",
                ephemeral=True,
            )

        if crush.id == ia.user.id:
            return await ia.response.send_message(
                "Some recommended reading: https://en.wikipedia.org/wiki/Narcissistic_personality_disorder",
                ephemeral=True,
            )

        await self.ensure_has_statistics(ia.user.id, crush.id, ia.guild_id)

        profile = await Profile.find_by_discord_id(ia.user.id)

        if crush.id in profile.crushes:
            return await ia.response.send_message(
                f"{crush.mention} is already in your list of crushes. If you like them this much, maybe you should send them a DM yourself.",
                ephemeral=True,
            )

        if await self.is_match_cached(ia.user.id, crush.id):
            return await ia.response.send_message(
                f"Calm down there, you already matched with {crush.mention} in the last 24 hours",
                ephemeral=True,
            )

        profile.crushes.append(crush.id)
        await profile.save()

        await ia.response.send_message(
            f"Added {crush.mention} to your list of crushes", ephemeral=True
        )

        if ia.user.id in crush_profile.crushes:
            await self.cache_match(ia.user.id, crush.id)

            user_dm_channel = ia.user.dm_channel
            if user_dm_channel is None:
                user_dm_channel = await ia.user.create_dm()

            await user_dm_channel.send(
                f"Congratulations! You and {crush.mention} like eachother!\nSend them a message with your best pickup line"
            )

            crush_dm_channel = crush.dm_channel
            if crush_dm_channel is None:
                crush_dm_channel = await crush.create_dm()

            await crush_dm_channel.send(
                f"Congratulations! You and {ia.user.mention} like eachother!\nSend them a message with your best pickup line"
            )

    @freudr_group.command(
        name="unlike", description="Remove someone from your list of crushes"
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def unlike(self, ia: Interaction, crush: Member):
        crush_profile = await Profile.find_by_discord_id(crush.id)

        if not crush_profile or not crush_profile.is_verified():
            return await ia.response.send_message(
                f"{crush.mention} is not verified, freudr commands only work on verified members",
                ephemeral=True,
            )

        if crush.id == ia.user.id:
            return await ia.response.send_message(
                "https://www.wikihow.com/Love-Yourself", ephemeral=True
            )

        await self.ensure_has_statistics(ia.user.id, crush.id, ia.guild_id)

        profile = await Profile.find_by_discord_id(ia.user.id)

        if crush.id not in profile.crushes:
            return await ia.response.send_message(
                f"I get that you don't like {crush.mention}, but they're not even in your list of crushes to begin with.",
                ephemeral=True,
            )

        profile.crushes.remove(crush.id)
        await profile.save()

        await ia.response.send_message(
            f"Removed {crush.mention} from your list of crushes", ephemeral=True
        )

    @freudr_group.command(
        name="list",
        description="See your list of crushes (only you will be able to see it)",
    )
    @app_commands.describe()
    @check_user_is_verified()
    async def show_list(self, ia: Interaction):
        profile = await Profile.find_by_discord_id(ia.user.id)

        await self.ensure_has_statistics(ia.user.id, ia.user.id, ia.guild_id)

        if not profile.crushes:
            return await ia.response.send_message(
                "You don't have any crushes, use '/freudr like <user>' to get started",
                ephemeral=True,
            )

        await ia.response.defer(thinking=True, ephemeral=True)

        matches = [
            f"- <@{crush_id}> ❤️‍🔥"
            for crush_id in profile.crushes
            if (crush := await Profile.find_by_discord_id(crush_id))
            and ia.user.id in crush.crushes
        ]

        crushes = [
            f"- <@{crush_id}>"
            for crush_id in profile.crushes
            if (crush := await Profile.find_by_discord_id(crush_id))
            and ia.user.id not in crush.crushes
        ]

        embeds = []
        if matches:
            embeds.append(Embed(title="Your Matches", description="\n".join(matches)))
        if crushes:
            embeds.append(Embed(title="Your Crushes", description="\n".join(crushes)))

        await ia.followup.send(embeds=embeds, ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Freudr(bot))
