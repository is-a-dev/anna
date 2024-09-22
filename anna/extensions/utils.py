import re
from nextcord.ext import commands
import nextcord

MAINTAINER_ROLE_ID = 830875873027817484

def extract_user_id(mention: str) -> str:
    match = re.match(r'<@!?(\d+)>', mention)
    if match:
        return match.group(1)
    return None


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

    @commands.command()
    @commands.has_role(MAINTAINER_ROLE_ID)
    async def send(
        self,
        ctx: commands.Context,
        channel: nextcord.TextChannel = None,
        *,
        message: str,
    ):
        """Send a message as Anna."""
        if channel and message:
            await channel.send(message)
        elif message:
            await ctx.send(message)
        else:
            await ctx.send("Please provide a message and channel to use this command.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        """Purges a specified number of messages."""

        # Ensure the number is a positive integer
        if amount <= 0:
            await ctx.send("Please specify a positive number of messages to purge.")
            return

        # Perform the purge
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Successfully purged {len(deleted)} messages.", delete_after=3)

    @commands.command(aliases=["setnick"])
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx: commands.Context, member: str = None, *, nickname: str = None):
        if member is None:
            member = ctx.author
        else:
            user_id = extract_user_id(member)
            if user_id:
                member = ctx.guild.get_member(int(user_id))
            else:
                member = nextcord.utils.get(ctx.guild.members, name=member) or nextcord.utils.get(ctx.guild.members, display_name=member)

        if member is None:
            await ctx.send("Member not found. Please provide a valid username or display name.")
            return
        if not member:
            await ctx.send("Please mention a member to change their nickname. Usage: `nick @member [nickname]`")
            return

        if member == ctx.author:
            await ctx.send("You can't change your own nickname using this command.")
            return

        if member == ctx.guild.owner:
            await ctx.send("You can't change the server owner's nickname.")
            return

        if member.top_role >= ctx.author.top_role:
            await ctx.send("You can't change the nickname of someone with a higher or equal role than yours.")
            return

        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("I can't change the nickname of someone with a higher or equal role than mine.")
            return

        if not nickname:
            nickname = member.name

        try:
            await member.edit(nick=nickname)
            await ctx.send(f"**{member.name}**'s nickname has been changed to **{nickname}**.")
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to change this member's nickname.")
        except nextcord.HTTPException:
            await ctx.send("An error occurred while trying to change the nickname.")

def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
