from __future__ import annotations

import re
from typing import List

import aiohttp
import nextcord
from nextcord.ext import commands


async def request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            return await ans.json()


# so my LSP know it

request.__doc__ = aiohttp.ClientSession.request.__doc__


FULL_MATCH_ANY_REPO = r"(https:\/\/github.com\/)?([A-Za-z1-9-]+)\/([A-Za-z1-9-]+)(\/pull)?(#|\/)(?P<pr_id>\d+)"


MATCH_IS_A_DEV_ONLY = r"register#(\d+)"
VERY_SHORT_MESSAGE = r"##(\d+)"
PR_CHANNEL_ID = 1130858271620726784
STAFF_ROLE_ID = 1197475623745110109


class _PRRawObject(object):
    def __init__(self, *, repo_owner: str, repo_name: str, pr_id: str) -> None:
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_id = pr_id


class GitHub(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # if message.channel.id != PR_CHANNEL_ID: return
        if message.author.bot:
            return
        full_matches: List[re.Match] = re.findall(FULL_MATCH_ANY_REPO, message.content)
        # print(full_matches)
        is_a_dev_matches: List[re.Match] = re.findall(  # noqa: F841
            MATCH_IS_A_DEV_ONLY, message.content
        )

        very_short_matches: List[re.Match] = re.findall(
            VERY_SHORT_MESSAGE, message.content
        )
        pr_list: List[_PRRawObject] = []
        if len(full_matches) > 0:
            for x in full_matches:
                if x[0] == "https://github.com/":
                    await message.edit(suppress=True)
                # print(x)
                repo_owner = x[1]
                repo_name = x[2]
                pr_id = x[5]
                pr_list.append(
                    _PRRawObject(
                        repo_owner=repo_owner, repo_name=repo_name, pr_id=pr_id
                    )
                )
        if len(very_short_matches) > 0:
            for x in very_short_matches:
                pr_id = x
                repo_owner = "is-a-dev"
                repo_name = "register"
                pr_list.append(
                    _PRRawObject(
                        repo_owner=repo_owner, repo_name=repo_name, pr_id=pr_id
                    )
                )

        # TODO: Fix is-a-dev-only regex

        if len(pr_list) == 0:
            if message.channel.id == PR_CHANNEL_ID:
                if message.author.get_role(STAFF_ROLE_ID) is None:  # type: ignore
                    await message.delete()

            return
        embed_description = """"""
        for pr in pr_list:
            i = await request(
                "GET",
                f"https://api.github.com/repos/{pr.repo_owner}/{pr.repo_name}/issues/{pr.pr_id}",
            )
            embed_description += f"[(#{pr.pr_id}) {i['title']}]({i['html_url']})\n"

        embed = nextcord.Embed(
            title="PR/Issue",
            description=embed_description,
            color=nextcord.Color.from_rgb(136, 225, 180),
        )
        if message.channel == PR_CHANNEL_ID:
            embed.set_footer(text="No other messages, even 'Please' or 'Thank you'.")
        await message.channel.send(embed=embed)

    # @nextcord.slash_command()
    # async def gh(self, interaction: nextcord.Interaction) -> None:
    #     pass


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GitHub())
