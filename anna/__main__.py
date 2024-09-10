from __future__ import annotations
from os import environ
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import os
import nextcord
from nextcord import ApplicationError, Game, Intents
from nextcord.ext import application_checks as ac
from nextcord.ext import commands, help_commands, tasks  # type: ignore
import asyncio
from extensions.help_forum.database import Database
import subprocess
from extensions.help_forum.config import DATABASE_PATH

class Bot(commands.Bot):
    def __init__(self, db_path: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = Database(db_path)
        self.persistent_views_added = False

    async def on_command_error(self, context: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.NotOwner):
            await context.send("Only Anna's maintainers can run this command.")
        elif isinstance(error, commands.UserInputError):
            await context.send("User input error.")
        elif isinstance(error, commands.CommandNotFound):
            await context.send("Command not found.")
        elif isinstance(error, commands.errors.DisabledCommand):
            await context.send("This command has been disabled by Anna's maintainers.")
        else:
            await context.send("An error was caught while attempting to run the command.")
            await super().on_command_error(context, error)

    async def on_application_command_error(self, interaction: nextcord.Interaction, exception: ApplicationError) -> None:
        if isinstance(exception, ac.ApplicationMissingRole):
            await interaction.send("You must be a staff member to use this command.")
        else:
            await interaction.send("An error was caught while attempting to run the command.")
            await super().on_application_command_error(interaction, exception)

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event triggered when the bot is ready """
        print(f'{self.user} is now online!')
        await self.db.create_tables()

bot = Bot(
    db_path=DATABASE_PATH,
    intents=Intents.all(),
    command_prefix="." if os.getenv("TEST") else "a?",
    help_command=help_commands.PaginatedHelpCommand(),
    case_insensitive=True,
    owner_ids=[716306888492318790, 961063229168164864],  # Cutedog and orangc
    allowed_mentions=nextcord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    activity=nextcord.Activity(
        type=nextcord.ActivityType.watching,
        name="is-a.dev",
        assets={"large_image": "is-a-dev"}
    )
)
    
extensions = ["extensions.help_forum.help_system", "extensions.antihoist", "extensions.fun", "extensions.faq", "extensions.antiphishing", "extensions.testing_functions", "extensions.nonsense", "extensions.dns", "extensions.suggestions", "extensions.delete_response", "extensions.github", "extensions.oneword", "extensions.utils", "extensions.tags", "extensions.ping_cutedog"]
if nextcord.version_info < (3, 0, 0):
    extensions.append("onami")
if os.getenv("HASDB"):
    extensions.append("extensions.tags_reworked")
for i in extensions:
    bot.load_extension(i)
bot.run(environ["TOKEN"])