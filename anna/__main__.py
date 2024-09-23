from __future__ import annotations
import os
import threading
import nextcord
from nextcord.ext import commands, help_commands, tasks
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from extensions.help_forum.database import HelpDatabase
from web import app

load_dotenv()

def run_flask():
    app.run(host="0.0.0.0", port=5000)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.hdb = HelpDatabase(os.getenv("MONGO"), "anna")
        self.persistent_views_added = False

    async def setup_database(self) -> None:
        """Setup MongoDB connection and collections"""
        if not os.getenv("HASDB"):
            raise Exception("No Mongo found")
        # Setup async MongoDB connection
        self.db_client = AsyncIOMotorClient(os.getenv("MONGO"))
        self.db = self.db_client.get_database("anna")

        # check if collections exist
        collections = await self.db.list_collection_names()
        if (
            "config" not in collections
            or "threads" not in collections
            or "helpban" not in collections
        ):
            # Ensure collections are created
            await self.db.create_collection("config")
            await self.db.create_collection("threads")
            await self.db.create_collection("helpban")
            await self.db.create_collection("tags")
            await self.db.create_collection("users")
            print("Database collections created")

    @commands.Cog.listener()
    async def on_ready(self):
        """Event triggered when the bot is ready"""
        print(f"{self.user} is now online!")

        # Ensure the database is set up
        await self.setup_database()

bot = Bot(
    intents=nextcord.Intents.all(),
    command_prefix=os.getenv("PREFIX"),
    case_insensitive=True,
    help_command=help_commands.PaginatedHelpCommand(),
    owner_ids=[
        961063229168164864,
        716306888492318790,
        598245488977903688,
    ],  # orangc, cutedog, andrew
    allowed_mentions=nextcord.AllowedMentions(
        everyone=False, roles=False, users=True, replied_user=True
    ),
    activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="is-a.dev"),
)

extensions = [
    "onami",
    "extensions.faq",
    "extensions.owner-utils",
    "extensions.suggestions",
    "extensions.oneword",
    "extensions.errors",
    "extensions.starboard",
    "extensions.listeners.ping_cutedog",
    "extensions.listeners.github",
    "extensions.listeners.antiphishing",
    "extensions.fun.fun",
    "extensions.fun.topic",
    "extensions.fun.anime",
    "extensions.fun.manga",
    "extensions.fun.ubdict",
    "extensions.util.utils",
    "extensions.util.roles",
    "extensions.util.snipe",
    "extensions.util.info",
    "extensions.util.screenshot",
    "extensions.util.subdomains",
    "extensions.util.dns",
]

if os.getenv("HASDB"):
    database_extensions = [
        "extensions.tags",
        "extensions.counting",
        "extensions.help_forum.help_system",
    ]
    for extension in database_extensions:
        extensions.append(extension)
for extension in extensions:
    bot.load_extension(extension)

if __name__ == "__main__":
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    bot.run(os.getenv("TOKEN"))
