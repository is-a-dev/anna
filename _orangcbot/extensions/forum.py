# INCOMPLETED

import nextcord
from nextcord.ext import commands


class Forum(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.group()
    @commands.is_owner()
    async def forum(self, ctx):
        pass

    @forum.command()
    @commands.is_owner()
    async def approve(self, ctx):
        await ctx.channel.edit(
            applied_tags=ctx.channel.applied_tags.append(
                nextcord.Object(id=1226381318124994631)
            )
        )

    @forum.command()
    @commands.is_owner()
    async def skill(self, ctx):
        await ctx.channel.edit(
            applied_tags=ctx.channel.applied_tags.append(
                nextcord.Object(id=1228574337725104138)
            )
        )

    @forum.command()
    @commands.is_owner()
    async def announcement(self, ctx):
        await ctx.channel.edit(
            applied_tags=ctx.channel.applied_tags.append(
                nextcord.Object(id=1228911583837687898)
            )
        )

    @forum.command()
    @commands.is_owner()
    async def question(self, ctx):
        await ctx.channel.edit(
            applied_tags=ctx.channel.applied_tags.append(
                nextcord.Object(id=1229050682808467478)
            )
        )


def setup(bot):
    bot.add_cog(Forum(bot))
