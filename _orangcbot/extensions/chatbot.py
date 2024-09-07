from __future__ import annotations

from dotenv import load_dotenv
from nextcord import Embed, Interaction, SlashOption, slash_command
from nextcord.ext import commands

load_dotenv()
from os import getenv

import aiohttp


async def request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            return await ans.json(content_type=None)


CHATBOT_SERVER_LINK: str = getenv("CHATBOT_SERVER_LINK")


class Chatbot(commands.Cog):
    @slash_command()
    async def llama(
        self,
        interaction: Interaction,
        question: str = SlashOption(
            description="What do you want to ask?", required=True
        ),
    ) -> None:
        await interaction.response.defer()
        r = await request("GET", CHATBOT_SERVER_LINK, headers={"question": question})

        await interaction.send(
            embed=Embed(
                title="Meta Llama 3 - Question", description=r["response"]["response"]
            )
        )


def setup(bot) -> None:
    bot.add_cog(Chatbot())
