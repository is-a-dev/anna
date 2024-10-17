import nextcord
from nextcord.ext import commands, menus
import os
import subprocess
from __main__ import extensions, extensions_blacklist, BOT_NAME, EMBED_COLOR


class GuildListMenu(menus.ListPageSource):
    def __init__(self, guilds):
        super().__init__(guilds, per_page=10)

    async def format_page(self, menu, guilds):
        embed = nextcord.Embed(
            title="Bot Guilds",
            description="\n".join(
                [f"`{i + 1}.` **{guild.name}** - {guild.member_count} members"
                 for i, guild in enumerate(guilds)]
            ),
            color=EMBED_COLOR
        )
        return embed

class GuildListView(nextcord.ui.View):
    def __init__(self, source):
        super().__init__()
        self.menu = menus.MenuPages(source=source, clear_items_after=True)
    
    @nextcord.ui.button(label="Previous", style=nextcord.ButtonStyle.grey)
    async def previous_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.menu.show_checked_page(self.menu.current_page - 1, interaction=interaction)
    
    @nextcord.ui.button(label="Next", style=nextcord.ButtonStyle.grey)
    async def next_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.menu.show_checked_page(self.menu.current_page + 1, interaction=interaction)

class OwnerUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="guilds")
    async def guilds(self, ctx: commands.Context):
        """Lists all guilds the bot is in, ranked from most members to least, paginated if necessary."""
        guilds = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)

        if len(guilds) > 10:
            # Paginated view if guild count is greater than 10
            menu = GuildListMenu(guilds=guilds)
            view = GuildListView(source=menu)
            await ctx.reply(embed=await menu.get_page(0), view=view, mention_author=False)
        else:
            # Single page for fewer than 10 guilds
            description = "\n".join(
                [f"`{i + 1}.` **{guild.name}** - {guild.member_count} members"
                 for i, guild in enumerate(guilds)]
            )
            embed = nextcord.Embed(
                title="Guilds the bot is in",
                description=description,
                color=EMBED_COLOR
            )
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.is_owner()
    async def disable(self, ctx: commands.Context, cmd: str):
        if cmd == "disable":
            await ctx.reply(
                "You cannot disable the disable command.", mention_author=False
            )
        else:
            command = self.bot.get_command(cmd)
            if command is None:
                await ctx.reply("Command not found.", mention_author=False)
                return
            command.enabled = False
            await ctx.reply(f"Successfully disabled `{command}`.", mention_author=False)

    @commands.command()
    @commands.is_owner()
    async def enable(self, ctx: commands.Context, cmd: str):
        if cmd == "disable":
            await ctx.reply(
                "You cannot disable the enable command.", mention_author=False
            )
        else:
            command = self.bot.get_command(cmd)
            if command is None:
                await ctx.reply("Command not found.", mention_author=False)
                return
            command.enabled = True
            await ctx.reply(f"Successfully enabled `{command}`.", mention_author=False)

    @commands.command(aliases=["maintainer", "perms"])
    async def owner(self, ctx: commands.Context):
        owner_names = []
        for owner_id in self.bot.owner_ids:
            owner = self.bot.get_user(owner_id) or await self.bot.fetch_user(owner_id)
            if owner:
                owner_names.append("**" + owner.display_name + "**")
            else:
                owner_names.append(f"Unknown User (ID: {owner_id})")

        is_owner = await self.bot.is_owner(ctx.author)
        owner_names_str = ", ".join(owner_names)
        if is_owner:
            await ctx.reply(
                f"You have maintainer level permissions when interacting with {BOT_NAME}. Current users who hold maintainer level permissions: {owner_names_str}",
                mention_author=False,
            )
        else:
            await ctx.reply(
                f"You are not a maintainer of {BOT_NAME}. Current users who hold maintainer-level permissions: {owner_names_str}",
                mention_author=False,
            )

    @commands.command(aliases=["rx"])
    @commands.is_owner()
    async def reload_exts(self, ctx: commands.Context, *args):
        if not args:
            failed_extensions = []

            for extension in extensions:
                if extension not in extensions_blacklist:
                    if extension in self.bot.extensions:
                        continue
                    try:
                        self.bot.reload_extension("extensions." + extension)
                    except Exception as e:
                        failed_extensions.append(f"{extension}: {e}")

            success_message = f"Successfully reloaded all extensions."
            if failed_extensions:
                error_message = (
                    f"\nReloaded all except the following extensions:\n"
                    + "\n".join(failed_extensions)
                )
                await ctx.reply(error_message, mention_author=False)
            else:
                await ctx.reply(
                    "Successfully reloaded all extensions.", mention_author=False
                )

        else:
            extension = args[0]
            if "extensions." + extension in self.bot.extensions:
                try:
                    self.bot.reload_extension("extensions." + extension)
                    await ctx.reply(
                        f"Successfully reloaded `extensions.{extension}`.",
                        mention_author=False,
                    )
                except Exception as error:
                    await ctx.reply(
                        f"Failed to reload `{extension}`: {error}", mention_author=False
                    )
            else:
                await ctx.reply(
                    f"Extension `extensions.{extension}` is not loaded.",
                    mention_author=False,
                )

    @commands.command(aliases=["rsc"])
    @commands.is_owner()
    async def reload_slash_command(self, ctx: commands.Context) -> None:
        await ctx.bot.sync_application_commands()
        await ctx.reply(
            "Successfully synced bot application commands.", mention_author=False
        )

    @commands.command(aliases=["ux"])
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, *args) -> None:
        cog = args[0]
        try:
            self.bot.unload_extension("extensions." + cog)
            await ctx.reply(
                f"Successfully unloaded `extensions.{cog}`.", mention_author=False
            )
        except commands.ExtensionNotLoaded:
            await ctx.reply(
                f"`extensions.{cog}` was already unloaded.", mention_author=False
            )

    @commands.command(aliases=["lx"])
    @commands.is_owner()
    async def load(self, ctx: commands.Context, *args) -> None:
        cog = args[0]
        try:
            self.bot.load_extension("extensions." + cog)
        except commands.ExtensionAlreadyLoaded:
            await ctx.reply(
                f"'extensions.{cog}' was already loaded.", mention_author=False
            )
        await ctx.reply(
            f"Successfully loaded `extensions.{cog}`.", mention_author=False
        )

    @commands.command()
    @commands.is_owner()
    async def pull(self, ctx: commands.Context):
        current_dir = os.getcwd()
        takina_dir = os.path.join(current_dir, "anna", "extensions", "takina")

        def run_git_pull(directory):
            try:
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout
            except subprocess.CalledProcessError as e:
                return e.stderr

        current_dir_result = run_git_pull(current_dir)
        takina_dir_result = run_git_pull(takina_dir)

        message = f"**Git Pull Results:**\n\n**Current Directory:**\n{current_dir_result}\n\n**anna/extensions/takina Directory:**\n{takina_dir_result}"

        await ctx.reply(message, mention_author=False)


class tOwnerUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["trx"])
    @commands.is_owner()
    async def treload_exts(self, ctx: commands.Context, *args):
        extension = args[0]
        if "extensions.takina.takina.cogs." + extension in self.bot.extensions:
            try:
                self.bot.reload_extension("extensions.takina.takina.cogs." + extension)
                await ctx.reply(
                    f"Successfully reloaded `extensions.takina.takina.cogs.{extension}`.",
                    mention_author=False,
                )
            except Exception as error:
                await ctx.reply(
                    f"Failed to reload `{extension}`: {error}", mention_author=False
                )
        else:
            await ctx.reply(
                f"Extension `extensions.takina.takina.cogs.{extension}` is not loaded.",
                mention_author=False,
            )

    @commands.command(aliases=["tux"])
    @commands.is_owner()
    async def tunload(self, ctx: commands.Context, *args) -> None:
        cog = args[0]
        try:
            self.bot.unload_extension("extensions.takina.takina.cogs." + cog)
            await ctx.reply(
                f"Successfully unloaded `extensions.takina.takina.cogs.{cog}`.",
                mention_author=False,
            )
        except commands.ExtensionNotLoaded:
            await ctx.reply(
                f"`extensions.takina.takina.cogs.{cog}` was already unloaded.",
                mention_author=False,
            )

    @commands.command(aliases=["tlx"])
    @commands.is_owner()
    async def tload(self, ctx: commands.Context, *args) -> None:
        cog = args[0]
        try:
            self.bot.load_extension("extensions.takina.takina.cogs." + cog)
        except commands.ExtensionAlreadyLoaded:
            await ctx.reply(
                f"'extensions.{cog}' was already loaded.", mention_author=False
            )
        await ctx.reply(
            f"Successfully loaded `extensions.takina.takina.cogs.{cog}`.",
            mention_author=False,
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(OwnerUtils(bot))
    bot.add_cog(tOwnerUtils(bot))
