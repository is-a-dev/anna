from __future__ import annotations
import os
from os import environ
import nextcord
from nextcord.ext import commands
from nextcord.ext import commands, help_commands, tasks
from nextcord.ext import application_checks as ac
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient  # Use motor for async MongoDB operations
import asyncio
from extensions.help_forum.database import HelpDatabase

# Load environment variables
load_dotenv()

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.hdb = HelpDatabase(os.getenv("MONGO"), "anna")
        self.persistent_views_added = False

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

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event triggered when the bot is ready """
        print(f'{self.user} is now online!')

        # Ensure the database is set up
        await self.setup_database()

# Define the bot
bot = Bot(
    intents=nextcord.Intents.all(),
    command_prefix="a!" if os.getenv("TEST") else "a?",
    case_insensitive=True,
    help_command=help_commands.PaginatedHelpCommand(),
    owner_ids=[716306888492318790, 961063229168164864, 598245488977903688],  # Example owner IDs
    allowed_mentions=nextcord.AllowedMentions(everyone=False, roles=False, users=True, replied_user=True),
    activity=nextcord.Activity(
        type=nextcord.ActivityType.watching,
        name="is-a.dev"
    )
)
    
extensions = ["errors", "extensions.help_forum.help_system", "extensions.antihoist", "extensions.fun", "extensions.faq", "extensions.antiphishing", "extensions.testing_functions", "extensions.nonsense", "extensions.dns", "extensions.suggestions", "extensions.delete_response", "extensions.github", "extensions.oneword", "extensions.utils", "extensions.tags", "extensions.ping_cutedog", "errors"]
if nextcord.version_info < (3, 0, 0):
    extensions.append("onami")
if os.getenv("HASDB"):
    extensions.append("extensions.tags_reworked")
for i in extensions:
    bot.load_extension(i)
bot.run(environ["TOKEN"])