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

import aiohttp
import dotenv
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

dotenv.load_dotenv()

# import os

import random
from random import choice
from typing import TYPE_CHECKING, List, Literal, Optional

_bonk_ans: List[str] = [
    "Ouch!",
    "That hurts!",
    "How dare you!",
    "Hey, what was that for?!",
    "That *cannot* have been necessary.",
    "Ow.. could you not?!",
]

class BonkView(nextcord.ui.View):
    if TYPE_CHECKING:
        message: Optional[nextcord.Message]

    def __init__(self, ctx: commands.Context):
        super().__init__()
        self._ctx: commands.Context = ctx
        self.message: Optional[nextcord.Message] = None

    def update_msg(self, msg: nextcord.Message):
        self.message = msg

    @nextcord.ui.button(label="Bonk!", style=nextcord.ButtonStyle.red)
    async def _bonk(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        # print(interaction.user.id)
        # print(self._ctx.author.id)
        if interaction.user.id == self._ctx.author.id:  # type: ignore[reportOptionalMemberAccess]
            await self.message.edit(content=choice(_bonk_ans))  # type: ignore[reportOptionalMemberAccess]
        else:
            await interaction.response.send_message("Fool", ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


async def request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            return await ans.json()


class Fun(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        latency = bot.latency

    @commands.command()
    async def bonk(self, ctx):
        """Bonk Anna. Please don't, she doesn't like it."""
        k = BonkView(ctx)
        msg = await ctx.send(content="No, don't press that..", view=k)
        k.update_msg(msg)


    @commands.command()
    async def ubdict(self, ctx: commands.Context, *, word: str):
        """Query Urban Dictionary. Contributed by vaibhav."""
        params = {"term": word}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.urbandictionary.com/v0/define", params=params
            ) as response:
                data = await response.json()
        if not data["list"]:
            return await ctx.send("No results found.")
        embed = nextcord.Embed(
            title=data["list"][0]["word"],
            description=data["list"][0]["definition"],
            url=data["list"][0]["permalink"],
            color=nextcord.Color.green(),
        )
        embed.set_footer(
            text=f"👍 {data['list'][0]['thumbs_up']} | 👎 {data['list'][0]['thumbs_down']} | Powered by: Urban Dictionary"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Ping the bot."""
        latency = round(self._bot.latency * 1000)
        await ctx.send(f"Success! Anna is awake. Ping: {latency}ms")


    @commands.command()
    async def httpcat(self, ctx: commands.Context, code: int = 406):
        """Fetch an HTTP Cat image from the http.cat API."""
        await ctx.send(f"https://http.cat/{code}")

    @commands.command(aliases=["you"])
    async def dog(self, ctx: commands.Context):
        """Fetch a Dog image from dog.ceo API."""
        k = await request("GET", "https://dog.ceo/api/breeds/image/random")
        await ctx.send(k["message"])

    @commands.command()
    async def shouldi(self, ctx: commands.Context, question: Optional[str] = None):
        """Answer a question using the yesno.wtf API."""
        r = await request("GET", "https://yesno.wtf/api")
        await ctx.send(f"answer: [{r['answer']}]({r['image']})")


class FunSlash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    @nextcord.slash_command()
    async def dog(self, interaction: Interaction):
        k = await request("GET", "https://dog.ceo/api/breeds/image/random")
        await interaction.send(k["message"])

    @nextcord.slash_command()
    async def httpcat(
        self,
        interaction: nextcord.Interaction,
        code: int = SlashOption(
            description="The HTTP code to fetch for", required=True
        ),
    ) -> None:
        await interaction.send(f"https://http.cat/{code}")

    @nextcord.slash_command()
    async def shouldi(
        self,
        interaction: nextcord.Interaction,
        question: str = SlashOption(
            description="What are you asking me for?", required=False
        ),
    ) -> None:
        r = await request("GET", "https://yesno.wtf/api")
        await interaction.send(f"answer: [{r['answer']}]({r['image']})")

    @nextcord.slash_command()
    async def ubdict(
        self,
        interaction: nextcord.Interaction,
        word: str = SlashOption(description="The word to search for", required=True),
    ) -> None:
        params = {"term": word}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.urbandictionary.com/v0/define", params=params
            ) as response:
                data = await response.json()
        if not data["list"]:
            await interaction.send("No results found.")
            return
        embed = nextcord.Embed(
            title=data["list"][0]["word"],
            description=data["list"][0]["definition"],
            url=data["list"][0]["permalink"],
            color=nextcord.Color.green(),
        )
        embed.set_footer(
            text=f"👍 {data['list'][0]['thumbs_up']} | 👎 {data['list'][0]['thumbs_down']} | Powered by: Urban Dictionary"
        )
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
    bot.add_cog(FunSlash(bot))
