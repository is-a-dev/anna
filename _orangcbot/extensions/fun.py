from __future__ import annotations

import aiohttp
import dotenv
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from psl_dns import PSL

dotenv.load_dotenv()

# import os

_psl = PSL()
import random
from random import choice
from typing import TYPE_CHECKING, List, Literal, Optional

_bonk_ans: List[str] = [
    "Ouch!",
    "It hurts!",
    "Ohh noooo",
    "Pleaseeeeeee don't hurt me...",
]
_morals: List[str] = ["Excellent", "Good", "Normal", "Bad", "Very bad"]
MAIN_SERVER_GUILD_ID: Literal[830872854677422150] = 830872854677422150
# _randommer_api_key = os.getenv("RANDOMMER_API_KEY")
# def has_randommer_api_key():
#    async def predicate(ctx: comamnds.Context):
#        return _randommer_api_key != None
#    return commands.check(predicate)

DEGENERATE_ROLE_ID: Literal[1238746465111642122] = 1238746465111642122


# async def _request_randommer(*, params, path):
#    async with aiohttp.ClientSession() as session:
#        async with session.get(f"https://randommer.io/api/{path}", params=params, headers={"X-Api-Key": _randommer_api_key}) as response:
#            return await response.json()
class _BattleInvitation:
    def __init__(self, uid1: int, uid2: int):
        self.id: str = str(uid1) + str(uid2)
        self.uid1: int = uid1
        self.uid2: int = uid2


class SlapConfirmView(nextcord.ui.View):
    def __init__(self, ctx: commands.Context, invitation: _BattleInvitation):
        super().__init__()
        self._ctx: commands.Context = ctx
        self._invitation: _BattleInvitation = invitation

    @nextcord.ui.button(label="Confirm Battle", style=nextcord.ButtonStyle.blurple)
    async def _confirm(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        if self._invitation.uid2 == interaction.user.id:  # type: ignore[reportOptionalMemberAccess]
            await self._ctx.send("Player 2 has accepted the Slappy Slappy battle.")
            self._ctx.bot.dispatch("battle_acceptance", self._invitation)
        else:
            await interaction.send(
                "You are not the invited competitor!", ephemeral=True
            )


# class SlapView(nextcord.ui.View):
#     if TYPE_CHECKING:
#         _message: Optional[nextcord.Message]
#
#     def __init__(self, *, invitation: _BattleInvitation, ctx: commands.Context):
#         super().__init__()
#         self._invitation = invitation
#         self._ctx: commands.Context = ctx
#         self._message: Optional[nextcord.Message] = None
#         self._user_1_count: int = 0
#         self._user_2_count: int = 0
#
#     async def timeout(self):
#         await asyncio.sleep(90)
#         self.children[0].disabled = True  # type: ignore[reportAttributeAccessIssue]
#         self.stop()
#
#     def set_message(self, message: nextcord.Message):
#         self.message = message
#
#     def determine_winner(self):
#         return (
#             self._invitation.uid1
#             if self._user_1_count > self._user_2_count
#             else self._invitation.uid2
#         )
#
#     @nextcord.ui.button(label="Slap!", style=nextcord.ButtonStyle.red)
#     async def _slap(
#         self, button: nextcord.ui.Button, interaction: nextcord.Interaction
#     ):
#         if interaction.user.id == self._invitation.uid1:  # type: ignore[reportOptionalMemberAccess]
#             self._user_1_count += 1
#             await interaction.response.defer()
#         if interaction.user.id == self._invitation.uid2:  # type: ignore[reportOptionalMemberAccess]
#             self._user_2_count += 1
#             await interaction.response.defer()
#         else:
#             await interaction.response.send_message(
#                 "You are not a competitor.", ephemeral=True
#             )
#


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


# class RandomView(nextcord.ui.View):
#    def __init__(self, ctx, randomwhat: str):
#        super().__init__()
#        self._ctx: commands.Context = _ctx
#        self._random = randomwhat
#        self.message: Optional[nextcord.Message] = None
#
#    def update_msg(self, msg: nextcord.Message):
#        self.message = msg

#    @nextcord.ui.button("Generate a new one?", style=nextcord.ButtonStyle.green)
#    async def _generator(
#            self, button: nextcord.ui.Button, interaction: nextcord.Interaction
#            ):
#        ...

# import copy


async def request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            return await ans.json()


class Fun(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.command()
    async def bonk(self, ctx):
        """Bonk me."""
        k = BonkView(ctx)
        msg = await ctx.send(content="Good.", view=k)
        k.update_msg(msg)

    @commands.command()
    async def areweinpsl(self, ctx):
        """Show whether PSL changes are deployed."""
        if _psl.is_public_suffix("is-a.dev"):
            await ctx.send("Yes, we are.")
        else:
            await ctx.send("No, we aren't.")

    @commands.command()
    async def ubdict(self, ctx: commands.Context, *, word: str):
        """Show urban dictionary query. Contributed by vaibhav."""
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

    # @commands.command()
    # @commands.is_owner()
    # async def slappy(self, ctx: commands.Context, *, user: nextcord.Member):
    #     inv = _BattleInvitation(ctx.author.id, user.id)
    #     await ctx.send(
    #         f"<@{int(user.id)}>, <@{int(ctx.author.id)}> has invited you to a Slappy Slappy game.",
    #         allowed_mentions=nextcord.AllowedMentions.none(),
    #         view=SlapConfirmView(ctx, inv),
    #     )
    #
    #     def check(m: _BattleInvitation):
    #         return m.id == inv.id
    #
    #     await ctx.bot.wait_for("battle_acceptance", check=check, timeout=60)
    #     k = SlapView(invitation=inv, ctx=ctx)
    #     end = datetime.datetime.now() + datetime.timedelta(seconds=90)
    #     i = await ctx.send(
    #         f"<@{int(inv.uid1)}> and <@{inv.uid2}> has gone for a Slappy Slappy game. Press the button to score. This game ends in {nextcord.utils.format_dt(end, style='R')}.",
    #         allowed_mentions=nextcord.AllowedMentions.none(),
    #         view=k,
    #     )
    #     await k.wait()
    #     winner = k.determine_winner()
    #     await i.edit(
    #         content=f"<@{inv.uid1}> and <@{inv.uid2}> played a Slappy Slappy game in which <@{winner}> was the winner. This game has ended in {nextcord.utils.format_dt(end)}.",
    #         allowed_mentions=nextcord.AllowedMentions.none(),
    #         view=k,
    #     )

    @commands.command()
    async def moral(
        self, ctx: commands.Context, member: Optional[nextcord.Member] = None
    ) -> None:
        """Show one's moral."""
        # state = ""
        if not member:
            member = ctx.author  # type: ignore[reportAssignmentType]
        if member.id == 716134528409665586:  # type: ignore[reportOptionalMemberAccess]
            state = "Paragon of Virtue"

        elif member.id == 853158265466257448:  # type: ignore[reportOptionalMemberAccess]
            state = "Beneath contempt"
        elif member.id == 961063229168164864:  # type: ignore[reportOptionalMemberAccess]
            state = "Degenerate"
        elif member.get_role(DEGENERATE_ROLE_ID):
            state = r"Degenerate\*"
        else:
            state = choice(_morals)

        await ctx.send(f"**{member.display_name}**'s moral status is **{state}**")  # type: ignore[reportOptionalMemberAccess]

    @nextcord.user_command(name="See moral")
    async def see_moral(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ) -> None:
        # state = ""
        if member.id == 716134528409665586:
            state = "Paragon of Virtue"
        elif member.id == 853158265466257448:
            state = "Beneath contempt"
        elif member.id == 961063229168164864:
            state = "Degenerate"
        elif member.get_role(DEGENERATE_ROLE_ID):
            state = r"Degenerate\*"
        else:
            state = choice(_morals)
        await interaction.response.send_message(
            f"**{member.display_name}**'s moral status is **{state}**"
        )

    @nextcord.slash_command()
    async def ping(self, interaction: nextcord.Interaction) -> None:
        """Am I alive?"""
        await interaction.response.send_message("No")

    @commands.command()
    async def fool(
        self, ctx: commands.Context, member: Optional[nextcord.Member] = None
    ) -> None:
        """Show the fool level of somebody."""
        if not member:
            member = ctx.author  # type: ignore[reportAssignmentType]
        if member.id == 716134528409665586:  # type: ignore[reportOptionalMemberAccess]
            level = 0
        # elif member.id == 853158265466257448:
        #     level = 99+3/4
        else:
            level = random.randint(0, 100)

        await ctx.send(f"**{member.display_name}** is {level}% a fool.")  # type: ignore[reportOptionalMemberAccess]

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
        """Answer your question using yesno.wtf API."""
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

    @nextcord.slash_command()
    async def moral(
        self,
        interaction: Interaction,
        member: nextcord.Member = SlashOption(
            description="The user you want to see the moral.", required=False
        ),
    ) -> None:
        if not member:
            member = interaction.user
        if member.id == 716134528409665586:
            state = "Paragon of Virtue"
        elif member.id == 853158265466257448:
            state = "Beneath contempt"
        elif member.id == 961063229168164864:
            state = "Degenerate"
        elif member.get_role(DEGENERATE_ROLE_ID):
            state = r"Degenerate\*"

        else:
            state = choice(_morals)
        await interaction.response.send_message(
            f"**{member.display_name}**'s moral status is **{state}**"
        )

    @nextcord.slash_command()
    async def fool(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.User = SlashOption(
            description="The member you want to see the fool level of.", required=False
        ),
    ) -> None:
        if not member:
            member = interaction.user
        if member.id == 716134528409665586:
            level = 0
        else:
            level = random.randint(0, 100)
        await interaction.send(f"{member.display_name} is {level}% a fool.")


def setup(bot):
    bot.add_cog(Fun(bot))
    bot.add_cog(FunSlash(bot))
