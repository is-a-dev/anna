import nextcord
from nextcord.ext import commands


class LoginButton(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(
            nextcord.ui.Button(
                label="Login",
                style=nextcord.ButtonStyle.primary,
                custom_id="login_button",
            )
        )


class Login(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")

    @commands.command()
    async def login(self, ctx):
        view = LoginButton()
        await ctx.send("Click the button to login:", view=view)


def setup(bot):
    bot.add_cog(Login(bot))
