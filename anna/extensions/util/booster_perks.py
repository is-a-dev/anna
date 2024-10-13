import nextcord
from nextcord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
import os

class CustomRoleManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.booster_role_id = 1197475623745110109  # Booster role ID
        self.position_role_id = 1111968864390107191  # Role ID to place new roles under
        self.db = AsyncIOMotorClient(os.getenv("MONGO")).get_database(os.getenv("DB_NAME"))

    async def user_has_bypass(self, guild_id: int, user_id: int):
        """Check if a user has been granted a boost bypass by an admin."""
        result = await self.db.bypass.find_one({"guild_id": guild_id, "user_id": user_id})
        return bool(result)

    async def set_bypass(self, guild_id: int, user_id: int, bypass: bool):
        """Set or remove bypass for a user."""
        if bypass:
            await self.db.bypass.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {"bypass": True}},
                upsert=True
            )
        else:
            await self.db.bypass.delete_one({"guild_id": guild_id, "user_id": user_id})

    async def get_custom_role(self, guild: nextcord.Guild, user: nextcord.Member):
        """Retrieve the user's custom role if they have one."""
        result = await self.db.custom_roles.find_one({"guild_id": guild.id, "user_id": user.id})
        if result:
            return guild.get_role(result["role_id"])
        return None

    async def create_custom_role(self, guild: nextcord.Guild, user: nextcord.Member):
        """Create a custom role for the user."""
        # Find the position of the desired role to place the new role under
        position_role = guild.get_role(self.position_role_id)
        position = position_role.position - 1 if position_role else len(guild.roles) - 1

        new_role = await guild.create_role(name=f"{user.name}'s Custom Role", position=position)
        await user.add_roles(new_role)

        await self.db.custom_roles.update_one(
            {"guild_id": guild.id, "user_id": user.id},
            {"$set": {"role_id": new_role.id}},
            upsert=True
        )
        return new_role

    async def delete_custom_role(self, guild: nextcord.Guild, user: nextcord.Member):
        """Delete the user's custom role if it exists."""
        custom_role = await self.get_custom_role(guild, user)
        if custom_role:
            await custom_role.delete()
            await self.db.custom_roles.delete_one({"guild_id": guild.id, "user_id": user.id})

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        """Check if a user stopped boosting and delete their custom role if they don't have bypass."""
        if before.guild.id != after.guild.id:
            return

        booster_role = nextcord.utils.get(after.guild.roles, id=self.booster_role_id)
        if booster_role not in after.roles and booster_role in before.roles:
            if not await self.user_has_bypass(after.guild.id, after.id):
                await self.delete_custom_role(after.guild, after)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bypass_boost(self, ctx: commands.Context, user: nextcord.Member, bypass: bool):
        """Grant or remove a boost bypass for a user."""
        await self.set_bypass(ctx.guild.id, user.id, bypass)
        status = "granted" if bypass else "revoked"
        await ctx.send(f"Boost bypass {status} for {user.mention}.")

    @commands.group(invoke_without_command=True)
    async def boostrole(self, ctx: commands.Context):
        """Group of commands to manage your custom role."""
        await ctx.send("Available subcommands: `create`, `name`, `colour`, `icon`.")

    @boostrole.command(name="create")
    async def create_custom_role(self, ctx: commands.Context):
        """Create a custom role for the user."""
        # Check if the user already has a custom role
        if await self.get_custom_role(ctx.guild, ctx.author):
            await ctx.send(":x: You already have a custom role.")
            return

        # Check if the user is a booster or has bypass
        booster_role = nextcord.utils.get(ctx.guild.roles, id=self.booster_role_id)
        if booster_role not in ctx.author.roles and not await self.user_has_bypass(ctx.guild.id, ctx.author.id):
            await ctx.send(":x: You must be boosting the server to create a custom role.")
            return

        # Create the role
        new_role = await self.create_custom_role(ctx.guild, ctx.author)
        await ctx.send(f"Your custom role `{new_role.name}` has been created!")

    @boostrole.command(name="name")
    async def set_custom_role_name(self, ctx: commands.Context, *, name: str):
        """Set the name of the user's custom role."""
        custom_role = await self.get_custom_role(ctx.guild, ctx.author)
        if custom_role is None:
            await ctx.send(":x: You don't have a custom role.")
            return

        await custom_role.edit(name=name)
        await ctx.send(f"Your custom role name has been changed to `{name}`.")

    @boostrole.command(name="colour")
    async def set_custom_role_colour(self, ctx: commands.Context, colour: nextcord.Colour):
        """Set the colour of the user's custom role."""
        custom_role = await self.get_custom_role(ctx.guild, ctx.author)
        if custom_role is None:
            await ctx.send(":x: You don't have a custom role.")
            return

        await custom_role.edit(colour=colour)
        await ctx.send(f"Your custom role colour has been changed to `{colour}`.")

    @boostrole.command(name="icon")
    async def set_custom_role_icon(self, ctx: commands.Context, icon: nextcord.Asset):
        """Set the icon of the user's custom role."""
        custom_role = await self.get_custom_role(ctx.guild, ctx.author)
        if custom_role is None:
            await ctx.send(":x: You don't have a custom role.")
            return

        await custom_role.edit(display_icon=icon)
        await ctx.send("Your custom role icon has been updated.")

def setup(bot: commands.Bot):
    bot.add_cog(CustomRoleManager(bot))
