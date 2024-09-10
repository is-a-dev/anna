from __future__ import annotations
import os
from os import environ
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient  # Use motor for async MongoDB operations
import asyncio

# Load environment variables
load_dotenv()

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = None
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

    async def setup_database(self) -> None:
        """ Setup MongoDB connection and collections """
        if not os.getenv("HASDB"):
            raise Exception("No Mongo found")
        # Setup async MongoDB connection
        self.db_client = AsyncIOMotorClient(os.getenv("MONGO"))
        self.db = self.db_client.get_database("anna")

        # check if collections exist
        collections = await self.db.list_collection_names()
        if "config" not in collections or "threads" not in collections or "helpban" not in collections:
            # Ensure collections are created
            await self.db.create_collection('config')
            await self.db.create_collection('threads')
            await self.db.create_collection('helpban')
            await self.db.create_collection('tags')
            await self.db.create_collection('users')
            print("Database collections created")

    async def on_ready(self):
        """ Event triggered when the bot is ready """
        print(f'{self.user} is now online!')

        # Ensure the database is set up
        await self.setup_database()
        print("Database connected")

# Define the bot
bot = Bot(
    intents=nextcord.Intents.all(),
    command_prefix="a!" if os.getenv("TEST") else "a?",
    case_insensitive=True,
    owner_ids=[716306888492318790, 961063229168164864, 598245488977903688],  # Example owner IDs
    allowed_mentions=nextcord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    activity=nextcord.Activity(
        type=nextcord.ActivityType.watching,
        name="is-a.dev"
    )
)
    
extensions = ["extensions.help_forum.help_system", "extensions.antihoist", "extensions.fun", "extensions.faq", "extensions.antiphishing", "extensions.testing_functions", "extensions.nonsense", "extensions.dns", "extensions.suggestions", "extensions.delete_response", "extensions.github", "extensions.oneword", "extensions.utils", "extensions.tags", "extensions.ping_cutedog", "errors"]
if nextcord.version_info < (3, 0, 0):
    extensions.append("onami")
if os.getenv("HASDB"):
    extensions.append("extensions.tags_reworked")
for i in extensions:
    bot.load_extension(i)
bot.run(environ["TOKEN"])
