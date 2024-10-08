import nextcord
from nextcord.ext import commands
import uuid
import os


class LoginButton(nextcord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        dynamic_uuid = str(uuid.uuid4())
        # get domain from environment variable
        domain = os.getenv("DOMAIN")

        # Store UUID, user ID, and set used to False
        self.bot.loop.create_task(self.store_uuid(dynamic_uuid, user_id))

        # Add the button as a URL button
        self.add_item(
            nextcord.ui.Button(
                label="Login",
                style=nextcord.ButtonStyle.link,  # Use link style for URL button
                url=f"https://{domain}/authenticate?code={dynamic_uuid}",  # URL with dynamic UUID
            )
        )

    async def store_uuid(self, dynamic_uuid, user_id):
        # Insert UUID and user ID into MongoDB with used=False
        await self.bot.db.login_data.insert_one(
            {"uuid": dynamic_uuid, "user_id": user_id, "used": False}
        )


class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")

    @commands.command()
    async def login(self, ctx):
        view = LoginButton(self.bot, ctx.author.id)
        await ctx.reply("Click the button to login:", view=view, mention_author=False)

    # Example of updating the `used` field to True after successful login
    async def mark_uuid_as_used(self, uuid):
        await self.bot.db.login_data.update_one(
            {"uuid": uuid}, {"$set": {"used": True}}
        )


def setup(bot):
    bot.add_cog(Login(bot))
