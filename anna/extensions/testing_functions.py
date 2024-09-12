# Copyright (c) 2024 - present, MaskDuck

import nextcord
from nextcord.ext import commands
import os
from __main__ import extensions

class Testings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def hinder(self, ctx: commands.Context, cmd: str):
        if cmd == "hinder":
            await ctx.send("You cannot hinder the hinder command.")
        else:
            command = self._bot.get_command(cmd)
            if command is None:
                await ctx.send("Command not found.")
                return
            command.enabled = not command.enabled
            await ctx.send("Successfully hindered ${cmd}.")

    @commands.command()
    @commands.is_owner()
    async def test_owner_perm(self, ctx: commands.Context):
        await ctx.send("You have owner level permissions when interacting with Anna.")
    
    @commands.command()
    @commands.is_owner()
    async def reload_exts(self, ctx: commands.Context, *args):
        if not args:
            reloaded_extensions = []
            failed_extensions = []

            if nextcord.version_info < (3, 0, 0):
                extensions.append("onami")
            if os.getenv("HASDB"):
                extensions.append("extensions.tags_reworked")

            for ext in extensions:
                try:
                    self._bot.reload_extension(ext)
                    reloaded_extensions.append(ext)
                except Exception as e:
                    failed_extensions.append(f"{ext}: {e}")

            success_message = f"Successfully reloaded all extensions."
            if failed_extensions:
                error_message = f"\nFailed to reload the following extensions:\n" + "\n".join(failed_extensions)
                await ctx.send(f"{success_message}{error_message}")
            else:
                await ctx.send(success_message)

        else:
            try:
                extension = args[0]
                self._bot.reload_extension(extension)
                await ctx.send(f"Successfully reloaded `{extension}`.")
            except Exception as e:
                await ctx.send(f"Failed to reload `{extension}`: {e}")

    @commands.command()
    @commands.is_owner()
    async def reload_slash_command(self, ctx: commands.Context) -> None:
        await ctx.bot.sync_application_commands()
        await ctx.send("Successfully synced bot application commands.")

    @commands.command()
    @commands.has_role(830875873027817484)
    async def disable_oneword_cog(self, ctx: commands.Context) -> None:
        try:
            self._bot.unload_extension("extensions.oneword")
        except commands.ExtensionNotLoaded:
            await ctx.send("The <#1225794824649838612> was already unloaded.")
        await ctx.send(
            "Successfully unloaded the <#1225794824649838612> cog."
        )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Testings(bot))
