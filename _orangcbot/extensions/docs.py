"""
The MIT License (MIT)

Copyright (c) 2021-present tag-epic

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# taken from https://github.com/nextcord/previous/blob/master/cogs/discorddoc.py
from typing import Any

import nextcord
from algoliasearch.search_client import SearchClient
from nextcord.ext import commands


class Docs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ## Fill out from trying a search on the ddevs portal
        app_id = "BH4D9OD16A"
        api_key = "f37d91bd900bbb124c8210cca9efcc01"
        self.search_client = SearchClient.create(app_id, api_key)
        self.index = self.search_client.init_index("discord")
        neovim_app_id = "X185E15FPG"
        neovim_api_key = "b5e6b2f9c636b2b471303205e59832ed"
        self.neovim_search_client = SearchClient.create(neovim_app_id, neovim_api_key)
        self.neovim_index = self.neovim_search_client.init_index("nvim")

    @nextcord.slash_command()
    async def nvim_doc(
        self,
        interaction: nextcord.Interaction,
        *,
        search_term: str = nextcord.SlashOption(
            description="The query to search with", required=True
        ),
    ) -> Any:
        """Need help with Neovim? We've got you covered!"""
        results = self.neovim_index.search(search_term)
        description = ""
        hits = []
        for hit in results["hits"]:

            title = self.get_level_str(hit.get("hierarchy"))
            title = title.replace("=", "")
            title = title.replace("-", "")
            hits.append(title)
            description += f"[{title}]({hit['url']})\n"
            if len(hits) > 10:
                break
        embed = nextcord.Embed(
            title="Your Neovim docs have arrived!",
            description=description,
            color=nextcord.Color.green(),
        )
        await interaction.send(embed=embed)

    @nextcord.slash_command()
    async def ddoc(self, interaction: nextcord.Interaction, *, search_term: str):
        """Query discord docs for... whatever you need."""
        results = self.index.search(search_term)
        description = ""
        hits = []
        for hit in results["hits"]:
            title = self.get_level_str(hit.get("hierarchy"))
            hits.append(title)
            url = hit["url"].replace(
                "https://discord.com/developers/docs", "https://discord.dev"
            )
            description += f"[{title}]({url})\n"
            if len(hits) == 10:
                break
        embed = nextcord.Embed(
            title="Your help has arrived!",
            description=description,
            color=nextcord.Color.blurple(),
        )
        await interaction.send(embed=embed)

    def get_level_str(self, levels):
        last = ""
        for level in levels.values():
            if level is not None:
                last = level
        return last


def setup(bot):
    bot.add_cog(Docs(bot))
