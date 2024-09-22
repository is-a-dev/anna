import nextcord
from nextcord.ext import commands
import re

def extract_user_id(mention: str) -> str:
    match = re.match(r'<@!?(\d+)>', mention)
    if match:
        return match.group(1)
    return None

class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="role", invoke_without_command=True)
    async def role(self, ctx: commands.Context):
        """Base role command, if no subcommand is passed."""
        await ctx.send("Please specify a subcommand: `add` or `remove`")

    @role.command(name="add")
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx: commands.Context, role: nextcord.Role, member: str = None):
        """Adds a role to a member."""
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

        try:
            await member.add_roles(role)
            await ctx.send(f"Added role `{role.name}` to **{member.display_name}**.")
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to add that role.")
        except nextcord.HTTPException as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @role.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx: commands.Context, role: nextcord.Role, member: str = None):
        """Removes a role from a member."""
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

        try:
            await member.remove_roles(role)
            await ctx.send(f"Removed role `{role.name}` from **{member.display_name}**.")
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to remove that role.")
        except nextcord.HTTPException as e:
            await ctx.send(f"An error occurred: {str(e)}")

    @role.error
    async def role_error(self, ctx: commands.Context, error):
        """Handle errors for the role command group."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to manage roles.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid role or user. Please mention the correct role and member.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")

def setup(bot):
    bot.add_cog(Roles(bot))
