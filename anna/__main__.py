#Copyright (c) 2024 - present, MaskDuck

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

#2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

#3. Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        super().__init__(*args, **kwargs)
        self.db = Database(db_path)

    async def on_command_error(
        self, context: commands.Context, error: commands.CommandError
    ) -> None:
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

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event triggered when the bot is ready """
        print(f'{self.user} is now online!')
        await self.db.create_tables()  # Ensure the database tables are created

    @tasks.loop(seconds=60)
    async def update(self):
        """ Task that runs every 60 seconds for periodic updates (if needed) """
        print("Performing periodic update...")  # Placeholder for actual task logic

owner_ids = [716306888492318790, 961063229168164864]  # Cutedog and orangc
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
bot.load_extension("extensions.purge")
bot.load_extension("extensions.ping_cutedog")
if os.getenv("HASDB"):
    bot.load_extension("extensions.tags_reworked")
bot.run(environ["TOKEN"])

if __name__ == "__main__":
    load_dotenv()
    bot = Bot(
        db_path=DATABASE_PATH,
        intents=intents,
        command_prefix=prefix
    )
    asyncio.run(bot.db.disconnect())