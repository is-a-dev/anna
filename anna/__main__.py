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

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event triggered when the bot is ready """
        print(f'{self.user} is now online!')
        await self.db.create_tables()

bot = Bot(
    db_path=DATABASE_PATH,
    intents=Intents.all(),
    command_prefix="a!" if os.getenv("TEST") else "a?",
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
    
extensions = ["extensions.help_forum.help_system", "extensions.antihoist", "extensions.fun", "extensions.faq", "extensions.antiphishing", "extensions.testing_functions", "extensions.nonsense", "extensions.dns", "extensions.suggestions", "extensions.delete_response", "extensions.github", "extensions.oneword", "extensions.utils", "extensions.tags", "extensions.ping_cutedog", "errors"]
if nextcord.version_info < (3, 0, 0):
    extensions.append("onami")
if os.getenv("HASDB"):
    extensions.append("extensions.tags_reworked")
for i in extensions:
    bot.load_extension(i)
bot.run(environ["TOKEN"])