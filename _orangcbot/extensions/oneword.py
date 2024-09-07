from __future__ import annotations

import asyncio
from typing import Final, cast

import nextcord
from nextcord.ext import commands

STAFF_ROLE_ID: Final[int] = 1197475623745110109
ONEWORD_CHANNEL_ID: Final[int] = 1225794824649838612


class Oneword(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    async def check_if_sending_consecutive_messages(
        self, channel: nextcord.TextChannel
    ):
        messages: list[nextcord.Message] = await channel.history(limit=2).flatten()
        return messages[1].author == messages[0].author

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message) -> None:
        if message.author.bot:
            return
        if message.author.get_role(STAFF_ROLE_ID):  # type: ignore[reportAttributeAccessIssue]
            return  # type: ignore[reportAttributeAccessIssue]
        if message.channel.id != ONEWORD_CHANNEL_ID:
            return
        ONEWORD_CHANNEL = cast(  # noqa: F841
            nextcord.TextChannel, self._bot.get_channel(ONEWORD_CHANNEL_ID)
        )

        # r = await self.check_if_sending_consecutive_messages(ONEWORD_CHANNEL)
        if " " in message.content or "\n" in message.content or "⠀" in message.content:
            await message.delete()
            s = await message.channel.send(
                "Message which have space(s) or newlines are not allowed."
            )
            await asyncio.sleep(5)
            await s.delete()
            return

        # if r:
        #     await message.delete()
        #     s = await message.channel.send("Nice try, kid.")
        #     await asyncio.sleep(5)
        #     await s.delete()
        #     return

        return

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: nextcord.Message, after: nextcord.Message
    ) -> None:
        if after.channel.id != ONEWORD_CHANNEL_ID:
            return
        if before.id != after.id:
            return
        if after.author.get_role(STAFF_ROLE_ID):  # type: ignore[reportAttributeAccessIssue]
            return  # type: ignore[reportAttributeAccessIssue]
        if " " in after.content:
            await after.delete()
            r = await after.channel.send("Good try, kid.")
            await asyncio.sleep(5)
            await r.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message) -> None:
        # audit_log = await message.guild.audit_logs(limit=1).flatten()
        # audit_log_entry: nextcord.AuditLogEntry = audit_log[0]
        # try:
        #     assert audit_log_entry.action == nextcord.AuditLogAction.message_delete
        # except AssertionError:
        #     return
        # if (
        #     (audit_log_entry.action == nextcord.AuditLogAction.message_delete)
        #     and (audit_log_entry.user == message.guild.me)
        #     and (audit_log_entry.extra.channel.id == ONEWORD_CHANNEL_ID)  # type: ignore
        # ):
        #     return
        if message.author.bot:
            return
        if " " in message.content:
            return
        if message.channel.id == ONEWORD_CHANNEL_ID:
            await message.channel.send(
                f"{message.author.mention}: {message.content}",
                allowed_mentions=nextcord.AllowedMentions.none(),
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Oneword(bot))
