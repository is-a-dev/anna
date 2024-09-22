import nextcord
from nextcord.ext import commands
import uuid


class LoginButton(nextcord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        dynamic_uuid = str(uuid.uuid4())

        # Store UUID, user ID, and set used to False
        self.bot.loop.create_task(self.store_uuid(dynamic_uuid, user_id))

        # Add the button as a URL button
        self.add_item(
            nextcord.ui.Button(
                label="Login",
                style=nextcord.ButtonStyle.link,  # Use link style for URL button
                url=f"https://anna-oauth.p2pb.dev/login?uuid={dynamic_uuid}"  # URL with dynamic UUID
            )
        )

    async def store_uuid(self, dynamic_uuid, user_id):
        # Insert UUID and user ID into MongoDB with used=False
        await self.bot.db.login_data.insert_one({
            "uuid": dynamic_uuid,
            "user_id": user_id,
            "used": False
        })


class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")

    @commands.command()
    async def login(self, ctx):
        view = LoginButton(self.bot, ctx.author.id)
        await ctx.send("Click the button to login:", view=view)

    # Example of updating the `used` field to True after successful login
    async def mark_uuid_as_used(self, uuid):
        await self.bot.db.login_data.update_one(
            {"uuid": uuid},
            {"$set": {"used": True}}
        )


def setup(bot):
    bot.add_cog(Login(bot))
