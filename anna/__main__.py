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
import logging
from extensions.help_forum.database import Database
import subprocess
from extensions.help_forum.config import DATABASE_PATH

prefix = "a!" if os.getenv("TEST") else "a?" # bot prefix, first value is for when the bot is in test mode, second is the general prefix

class Bot(commands.Bot):
    def __init__(self, db_path: str, *args, **kwargs) -> None:
        # self._db: psycopg2.connection = psycopg2.connect(
        #     host=getenv("DBHOST"),
        #     user=getenv("DBUSER"),
        #     port=getenv("DBPORT"),
        #     password=getenv("DBPASSWORD"),
        #     dbname=getenv("DBNAME"),
        # )
        super().__init__(*args, **kwargs)

    async def on_command_error(
        self, context: commands.Context, error: commands.CommandError
    ) -> None:
        self.persistent_views_added = False
        self.db = Database(db_path)
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

    async def on_application_command_error(
        self, interaction: nextcord.Interaction, exception: ApplicationError
    ) -> None:
        if isinstance(exception, ac.ApplicationMissingRole):
            await interaction.send("You must be a staff member to use this command.")
        else:
            await interaction.send("An error was caught while attempting to run the command.")
            await super().on_application_command_error(interaction, exception)
    @tasks.loop(seconds=60)
    async def on_ready(self):
        await self.db.create_tables()
        self.update.start()



owner_ids = [716306888492318790 , 961063229168164864] # cutedog and orangc
intents = Intents.all()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False
intents.integrations = False
intents.invites = False
intents.voice_states = False
intents.scheduled_events = False

bot = Bot(
    db_path=DATABASE_PATH,
    intents=intents,
    command_prefix=prefix,
    help_command=help_commands.PaginatedHelpCommand(),
    case_insensitive=True,
    owner_ids=owner_ids,
    allowed_mentions=nextcord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    activity=nextcord.Activity(
        type=nextcord.ActivityType.watching, 
        name="is-a.dev",                      
        assets={"large_image": "is-a-dev"}    
    )
)

# TODO: Remove onami when nextcord 3.0 release
# WARNING: Do not remove this if!
if nextcord.version_info < (3, 0, 0):
    bot.load_extension("onami")

bot.load_extension("extensions.help_forum.help_system")
bot.load_extension("extensions.antihoist")
bot.load_extension("extensions.fun")
bot.load_extension("extensions.faq")
bot.load_extension("extensions.antiphishing")
bot.load_extension("extensions.testing_functions")
bot.load_extension("extensions.nonsense")
bot.load_extension("extensions.dns")
bot.load_extension("extensions.suggestions")
bot.load_extension("extensions.delete_response")
bot.load_extension("extensions.github")
bot.load_extension("extensions.oneword")
bot.load_extension("extensions.sender")
bot.load_extension("extensions.tags")
bot.load_extension("extensions.ping_cutedog")
if os.getenv("HASDB"):
    bot.load_extension("extensions.tags_reworked")
bot.run(environ["TOKEN"])

if __name__ == "__main__":
    load_dotenv()
    bot = Bot(
        DATABASE_PATH,
    )
    asyncio.run(bot.db.disconnect())