# Copyright (c) 2024 - present, MaskDuck

from __future__ import annotations
import urllib.parse
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
from random import randint

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
        if interaction.user.id == self._ctx.author.id:  # type: ignore[reportOptionalMemberAccess]
            await self.message.edit(content=choice(_bonk_ans))  # type: ignore[reportOptionalMemberAccess]
        else:
            await interaction.send("Only those who invoke the bonk command may bonk me. Actually, hey, stop bonking me at all!", ephemeral=True)

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
    
    @commands.command(name="avatar")
    async def avatar(self, ctx: commands.Context, member: nextcord.Member = None):
        member = member or ctx.author
        embed = nextcord.Embed(title=f"{member.name}'s Avatar", color=nextcord.Color.blue())
        embed.set_image(url=member.avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context):
        number = random.randint(1, 100)
        embed = nextcord.Embed(
            title="What number did you role?",
            description=f"You rolled a {number}!",
            color=nextcord.Color.blue()
        )
        await ctx.reply(embed=embed, mention_author=False)
        
    @commands.command(name="google")
    async def google(self, ctx: commands.Context, *, query: str):
        query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={query}"
        await ctx.reply(f"Here are the Google search results for: {query}\n{url}", mention_author=False)

    @commands.command()
    async def bonk(self, ctx):
        """Bonk Anna. Please don't, she doesn't like it."""
        k = BonkView(ctx)
        msg = await ctx.reply(content="No, don't press that..", view=k, mention_author=False)
        k.update_msg(msg)

    @commands.command()
    async def httpcat(self, ctx: commands.Context, code: int = 406):
        """Fetch an HTTP Cat image from the http.cat API."""
        await ctx.reply(f"https://http.cat/{code}", mention_author=False)

    @commands.command()
    async def shouldi(self, ctx: commands.Context, question: Optional[str] = None):
        """Answer a question using the yesno.wtf API."""
        r = await request("GET", "https://yesno.wtf/api")
        await ctx.reply(f"answer: [{r['answer']}]({r['image']})", mention_author=False)


class FunSlash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot

    @nextcord.slash_command(name="avatar")
    async def slash_avatar(self, interaction: nextcord.Interaction, member: nextcord.Member = SlashOption(
            description="The user whose avatar you would like to fetch", required=False
        )):
        member = member or ctx.author
        embed = nextcord.Embed(title=f"{member.name}'s Avatar", color=nextcord.Color.blue())
        embed.set_image(url=member.avatar.url)
        await interaction.send(embed=embed, mention_author=False)

    @nextcord.slash_command(name="roll", description="Roll a number!")
    async def slash_roll(self, interaction: nextcord.Interaction):
        number = random.randint(1, 100)
        embed = nextcord.Embed(
            title="What number did you role?",
            description=f"You rolled a {number}!",
            color=nextcord.Color.blue()
        )
        await interaction.send(embed=embed)
        
    @nextcord.slash_command(name="google")
    async def slash_google(self, interaction: nextcord.Interaction, *, query: str = SlashOption(
            description="Your search query", required=True
        )):
        query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={query}"
        await interaction.send(f"Here are the Google search results for: {query}\n{url}")

    @nextcord.slash_command(name="httpcat")
    async def slash_httpcat(
        self,
        interaction: nextcord.Interaction,
        code: int = SlashOption(
            description="The HTTP code to fetch for", required=True
        ),
    ) -> None:
        await interaction.send(f"https://http.cat/{code}")

    @nextcord.slash_command(name="shouldi")
    async def slash_shouldi(
        self,
        interaction: nextcord.Interaction,
        question: str = SlashOption(
            description="What are you asking me for?", required=False
        ),
    ) -> None:
        r = await request("GET", "https://yesno.wtf/api")
        await interaction.send(f"answer: [{r['answer']}]({r['image']})")

def setup(bot):
    bot.add_cog(Fun(bot))
    bot.add_cog(FunSlash(bot))
