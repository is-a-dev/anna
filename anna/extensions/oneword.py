"""
BSD 3-Clause License

Copyright (c) 2024 - present, MaskDuck

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

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

        if " " in message.content or "\n" in message.content or "⠀" in message.content:
            await message.delete()
            s = await message.channel.send(
                "Message which have space(s) or newlines are not allowed."
            )
            await asyncio.sleep(5)
            await s.delete()
            return

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
