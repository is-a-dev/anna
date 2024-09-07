# ruff: noqa
from nextcord.ext import commands

nohelp = """
This is not a help channel!\n
We have a help channel for a reason, see <#1228996111390343229>.\n
Please use that for help. Open a thread, even if it is a tiny problem.\n
So... **Enjoy troll answers past this message and take them with a pinch of salt. The action of following any help in this channel past this message is at your own risk. You've been warned.**\n
Please read the [is-a.dev docs](https://www.is-a.dev/docs/)\n
Have fun!"""

waittime = """
Us maintainers have a life; we aren't obligated to merge your PRs the moment you make your PR.\n
We have other things to do. This project is run by volunteers, so please have patience with us.\n
Instead of pinging us, send a PR in <#1130858271620726784> *once* and wait for us to review it.
"""

rtfm = """
Please read the documentation. It exists for a reason.\n
Our maintainers and helpers are volunteers. It's not our job to answer questions already answered in the documentation or FAQ.\n
- [is-a.dev documentation](https://is-a.dev/docs)\n
- <#991779321758896258>\n
"""
domservice = """
is-a.dev can give you support with your ***domain***, and on the condition that you've read the [documentation](https://is-a.dev/docs).\n
We do __not__ provide support for anything else. We aren't an HTML boot camp, and it's not our job to teach you JSON. We also don't provide support for Github or DNS questions either.
"""


class Tags(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.command()
    async def nohelp(self, ctx):
        if not ctx.channel.id in [1155589227728339074]:
            embed = nextcord.Embed(
                title="This is not a help channel.",
                description=nohelp,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)
        else:
            msg = await ctx.send("You fool.")
            await msg.delete()

    @commands.command()
    async def waittime(self, ctx):
        if True:  # blame orangc
            embed = nextcord.Embed(
                title="How long is it until my PR is merged?",
                description=waittime,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def rtfm(self, ctx):
        if True:
            embed = nextcord.Embed(
                title="Read The Fucking Manual",
                description=rtfm,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)

    @commands.command()
    async def domservice(self, ctx):
        if True:
            embed = nextcord.Embed(
                title="We're a domain service, and we provide support for domains",
                description=domservice,
                color=nextcord.Colour.red(),
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
