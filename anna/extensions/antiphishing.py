#Copyright (c) 2024 - present, MaskDuck

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

import asyncio
import re
import urllib.parse

import aiohttp
import nextcord
from nextcord.ext import commands


class AntiPhish(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        links = re.findall(r"(https?://[^\s]+)", message.content)
        for link in links:
            async with aiohttp.ClientSession() as session:
                host = urllib.parse.urlparse(link).hostname
                async with session.get(
                    f"https://api.phisherman.gg/v1/domains/{host}"
                ) as answer:
                    r = await answer.text()
                    # print(r)
                    if r == "true":
                        await self._bot.get_channel(955105139461607444).send(  # type: ignore[reportAttributeAccessIssue]
                            embed=nextcord.Embed(
                                title="Phishing found",
                                description=f"Message sender: {message.author.id}, original content: ```{message.content}```",
                                color=nextcord.Color.blue(),
                            )
                        )
                        await message.delete()
                        break

            await asyncio.sleep(1.5)


def setup(bot):
    bot.add_cog(AntiPhish(bot))
