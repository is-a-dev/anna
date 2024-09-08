from __future__ import annotations

from typing import Final, List, Optional, Tuple

import nextcord
from nextcord import Embed
from nextcord.ext import commands, menus

RULES: Final[List[str]] = [
    "Follow Discord's ToS and Community Guidelines.",
    "Do not ping maintainers to merge your pull request or other things.",
    (
        "Do not beg for your pull request to be merged"
        "we have other things to do and cannot just be merging PRs all day. "
        "Send them in <#1130858271620726784> **once**."
    ),
    "Be kind and respectful to others.",
    "No advertising except in <#1064140107659092060>.",
    "No NSFW (18+) content.",
    "Try not to get into heated discussions and cause chaos.",
    (
        "No spoon feeding users. People need to learn to read documentation on their own."
        "- If you open a thread about how to register a domain or similar you will be muted. "
        "**Read the documentation.**"
    ),
    "Maintainers have the right to remove you from specific programs or roles without notice.",
    "No asking for support in channels such as <#830872854677422153> or <#1057228967972716584>. We have a support forum for that <#1155589227728339074>.",
    "No bypassing mutes or bans.",
]

FOOTER: Final[str] = (
    "Maintainers will always have the final say, whether you agree with it or not. A maintainer's say is above the rules. "
    "We will moderate at our discretion, do not DM maintainers or helpers asking to be unmuted/unbanned."
)


class RulesPageSource(menus.ListPageSource):
    async def format_page(self, menus: menus.Menu, page: Tuple[int, str]) -> Embed:
        rulenum, ruleinfo = page
        embed = nextcord.Embed(
            title=f"Rule {rulenum+1}",
            description=f"{ruleinfo}\n\n**Please also note:**\n{FOOTER}",
            color=nextcord.Color.blue(),
        )
        return embed

    def get_max_pages(self):
        return len(self.entries)

    async def get_page(self, page_number: int) -> Tuple[int, str]:
        return (page_number, self.entries[page_number])


class RulesMenu(menus.ButtonMenuPages):
    def __init__(self):
        super().__init__(
            RulesPageSource(RULES, per_page=1), nextcord.ButtonStyle.primary
        )


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()
    async def rules(self, ctx: commands.Context, rulenum: Optional[int]):
        if rulenum:
            embed = nextcord.Embed(
                title=f"Rule {rulenum}",
                description=f"{RULES[rulenum-1]}\n\n**Please also note:**\n{FOOTER}",
                color=nextcord.Color.blue(),
            )
            await ctx.send(embed=embed)
            return
        await RulesMenu().start(ctx=ctx)


def setup(bot: commands.Bot):
    bot.add_cog(Rules(bot))
