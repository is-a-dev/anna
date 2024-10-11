from __main__ import Bot
import nextcord
from nextcord.ext import commands
import extensions.help_forum.config
import asyncio
from __main__ import EMBED_COLOR

config = extensions.help_forum.config


class NoGuildConfig(Exception):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        super().__init__(f"No configuration found for guild id {guild_id}")


class NoThreadFound(Exception):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(f"No thread found with id {thread_id}")


class AlreadyClosed(Exception):
    def __init__(self, thread_id: int):
        self.thread_id = thread_id
        super().__init__(f"Thread with id {thread_id} is already closed")


class LinkView(nextcord.ui.View):
    def __init__(self, label: str, link: str):
        super().__init__()
        self.add_item(
            nextcord.ui.Button(style=nextcord.ButtonStyle.link, label=label, url=link)
        )


class ConfirmView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.grey)
    async def cancel(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.send("Cancelled.", ephemeral=True)
        self.value = False
        self.stop()


class OpenHelpView(nextcord.ui.View):
    def __init__(self, bot: Bot, open_help_func: callable):
        super().__init__(timeout=None)
        self.bot = bot
        self.open_help_func = open_help_func

    @nextcord.ui.button(
        label=config.VIEW_OPEN_LABEL,
        style=nextcord.ButtonStyle.green,
        custom_id="open_help",
    )
    async def open_help(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        is_help_banned = await self.bot.hdb.get_helpban_user(
            interaction.user.id, interaction.guild.id
        )
        user_threads = await self.bot.hdb.get_user_threads(interaction.user.id)
        open_user_threads = [thread for thread in user_threads if not thread["closed"]]
        print(len(open_user_threads), open_user_threads)
        if len(open_user_threads) >= config.USER_THREAD_LIMIT:
            await interaction.send(
                f"You have reached the maximum open threads limit of {config.USER_THREAD_LIMIT}. You currently have {len(open_user_threads)} threads open.",
                ephemeral=True,
            )
            return
        if is_help_banned:
            await interaction.send(
                "You are help banned and cannot open a help thread.", ephemeral=True
            )
            return
        confirm_view = ConfirmView()
        await interaction.send(
            "Are you sure you want to open a help thread?",
            view=confirm_view,
            ephemeral=True,
        )
        await confirm_view.wait()
        if confirm_view.value is None:
            await interaction.send("Timed out.", ephemeral=True)
            return
        elif not confirm_view.value:
            await interaction.send("Cancelled.", ephemeral=True)
            return
        thread: nextcord.Thread = await self.open_help_func(interaction.user)
        await interaction.send(f"Created help thread {thread.mention}.", ephemeral=True)


class CloseHelpView(nextcord.ui.View):
    def __init__(self, close_help_func: callable, is_thread_author: callable):
        super().__init__(timeout=None)
        self.close_help_func = close_help_func
        self.is_thread_author = is_thread_author

    @nextcord.ui.button(
        label=config.VIEW_CLOSE_LABEL,
        style=nextcord.ButtonStyle.red,
        custom_id="close_help",
    )
    async def close_help(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)

        # check if it is a help thread author, or a staff member.
        if (
            not await self.is_thread_author(interaction.channel.id, interaction.user.id)
        ) and (not interaction.user.get_role(1197475623745110109)):
            await interaction.send(
                "You are not the author of this thread.", ephemeral=True
            )
            return
        await interaction.send("Closing help thread.", ephemeral=True)
        await self.close_help_func(interaction.channel.id)


class Help(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def is_thread_author(self, thread_id: int, user_id: int) -> bool:
        thread_data = await self.bot.hdb.get_thread(thread_id)
        if not thread_data:
            raise NoThreadFound(thread_id)
        return thread_data["author_id"] == user_id

    async def create_help_thread(self, member: nextcord.Member) -> nextcord.Thread:
        guild_config = await self.bot.hdb.get_config(member.guild.id)
        if not guild_config:
            raise NoGuildConfig(member.guild.id)
        placeholders = {
            "member.mention": member.mention,
            "member.name": member.name,
            "member.id": str(member.id),
        }
        forum: nextcord.ForumChannel = nextcord.utils.get(
            member.guild.channels, id=guild_config["help_forum_id"]
        )
        thread_name = config.replace_placeholders(config.THREAD_NAME, placeholders)
        embed_title = config.replace_placeholders(
            config.THREAD_EMBED_TITLE, placeholders
        )
        embed_description = config.replace_placeholders(
            config.THREAD_EMBED_DESCRIPTION, placeholders
        )

        embed = nextcord.Embed(title=embed_title, color=EMBED_COLOR)
        embed.description = embed_description
        embed.add_field(name="Resources", value=config.THREAD_EMBED_RESOURCES)
        close_view = CloseHelpView(self.close_help_thread, self.is_thread_author)
        thread = await forum.create_thread(
            name=thread_name, embed=embed, view=close_view
        )
        thread_open_message: nextcord.Message = await thread.fetch_message(thread.id)
        await thread_open_message.pin()
        await self.bot.hdb.create_thread(
            thread.id, member.guild.id, forum.id, member.id
        )
        return thread

    async def close_help_thread(self, thread_id: int) -> None:
        thread_data = await self.bot.hdb.get_thread(thread_id)
        if not thread_data:
            raise NoThreadFound(thread_id)
        guild = self.bot.get_guild(thread_data["guild_id"])
        forum = nextcord.utils.get(guild.channels, id=thread_data["help_forum_id"])
        thread: nextcord.Thread = nextcord.utils.get(forum.threads, id=thread_id)
        if thread_data["closed"]:
            raise AlreadyClosed(thread.id)
        thread_author = guild.get_member(thread_data["author_id"])
        placeholders = {
            "member.mention": thread_author.mention,
            "member.name": thread_author.name,
            "member.id": str(thread_author.id),
            "thread.name": thread.name,
            "thread.mention": thread.mention,
        }
        thread_close_msg = config.replace_placeholders(
            config.THREAD_CLOSE_MSG, placeholders
        )
        thread_close_dm = config.replace_placeholders(
            config.THREAD_CLOSE_DM, placeholders
        )
        await thread.send(thread_close_msg)
        try:
            thread_jump_view = LinkView("Jump to Thread", thread.jump_url)
            await thread_author.send(thread_close_dm, view=thread_jump_view)
        except Exception:
            pass
        await asyncio.sleep(
            1
        )  # To prevent message being sent after thread being closed on rare occasions
        if config.THREAD_CLOSE_LOCK:
            await thread.edit(locked=True)
        await thread.edit(archived=True)
        await self.bot.hdb.close_thread(thread_id)

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True)
    )
    async def help_setup(
        self,
        interaction: nextcord.Interaction,
        help_channel: nextcord.ForumChannel = nextcord.SlashOption(
            description="The channel to set as the help channel."
        ),
        role: nextcord.Role = nextcord.SlashOption(
            description="The role to set as the ping role."
        ),
    ):
        """Sets up the help system for the guild."""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if guild_config:
            embed = nextcord.Embed(
                description=config.SETUP_HELP_ALREADY, color=EMBED_COLOR
            )
            await interaction.send(embed=embed)
            return
        await self.bot.hdb.set_config(interaction.guild.id, help_channel.id, role.id)
        embed = nextcord.Embed(description=config.SETUP_HELP_SUCCESS, color=EMBED_COLOR)
        await interaction.send(embed=embed)

    @nextcord.slash_command()
    async def show_help_config(self, interaction: nextcord.Interaction):
        """Shows the current help system configuration."""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if not guild_config:
            raise NoGuildConfig(interaction.guild.id)
        help_channel = nextcord.utils.get(
            interaction.guild.channels, id=guild_config["help_forum_id"]
        )
        help_ping_role = nextcord.utils.get(
            interaction.guild.roles, id=guild_config["ping_role_id"]
        )
        embed = nextcord.Embed(title="Help System Configuration", color=EMBED_COLOR)
        embed.add_field(name="Help Channel", value=help_channel.mention)
        embed.add_field(name="Ping Role", value=help_ping_role.mention)
        await interaction.send(embed=embed)

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True),
        name="set_channel",
    )
    async def set_help_channel(
        self,
        interaction: nextcord.Interaction,
        help_channel: nextcord.ForumChannel = nextcord.SlashOption(
            description="The channel to set as the help channel."
        ),
    ):
        """Sets the help channel for the guild."""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if not guild_config:
            raise NoGuildConfig(interaction.guild.id)
        await self.bot.hdb.update_config(
            interaction.guild.id, help_channel.id, guild_config["ping_role_id"]
        )
        await interaction.send(f"Set help channel to {help_channel.mention}.")

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True),
        name="set_role",
    )
    async def help_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            description="The role to set as the ping role."
        ),
    ):
        """Sets the ping role for the help system."""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if not guild_config:
            raise NoGuildConfig(interaction.guild.id)
        await self.bot.hdb.update_config(
            interaction.guild.id, guild_config["help_forum_id"], role.id
        )
        await interaction.send(
            f"Set ping role to {role.mention}.",
            allowed_mentions=nextcord.AllowedMentions.none(),
        )

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True)
    )
    async def sendembed(
        self, interaction: nextcord.Interaction, title: str, description: str
    ):
        """Sends an embed with the specified title and description."""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if not guild_config:
            raise NoGuildConfig(interaction.guild.id)
        embed = nextcord.Embed(title=title, description=description, color=EMBED_COLOR)
        view = OpenHelpView(self.bot, self.create_help_thread)
        await interaction.send("As you say, master.", delete_after=3)
        await interaction.channel.send(embed=embed, view=view)

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True)
    )
    async def title(
        self,
        interaction: nextcord.Interaction,
        new_title: str = nextcord.SlashOption(
            description="The new title for the help thread."
        ),
    ):
        """Changes the title of the help thread. (MOD ONLY)"""
        await interaction.response.defer()
        guild_config = await self.bot.hdb.get_config(interaction.guild.id)
        if not guild_config:
            raise NoGuildConfig(interaction.guild.id)
        thread_info = await self.bot.hdb.get_thread(interaction.channel.id)
        if not thread_info:
            raise NoThreadFound(interaction.channel.id)
        thread_author = interaction.guild.get_member(thread_info["author_id"])
        forum: nextcord.ForumChannel = nextcord.utils.get(
            interaction.guild.channels, id=guild_config["help_forum_id"]
        )
        thread: nextcord.Thread = nextcord.utils.get(
            forum.threads, id=interaction.channel.id
        )
        if not thread:
            raise NoThreadFound(interaction.channel.id)
        new_title = f"{new_title} ({thread_author.name})"
        embed = nextcord.Embed(title="Title Change")
        embed.add_field(name="Old", value=thread.name, inline=False)
        embed.add_field(name="New", value=new_title, inline=False)
        await thread.edit(name=new_title)
        await interaction.send(embed=embed)

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_messages=True)
    )
    async def close(self, interaction: nextcord.Interaction):
        """Closes the help thread. (MOD ONLY)"""
        await interaction.response.defer(ephemeral=True)
        await interaction.send("Closing help thread.", ephemeral=True)
        await self.close_help_thread(interaction.channel.id)

    @nextcord.slash_command(
        default_member_permissions=nextcord.Permissions(manage_guild=True)
    )
    async def helpban(self, interaction: nextcord.Interaction):
        pass

    @helpban.subcommand(name="list")
    async def helpban_list(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        helpban_list = await self.bot.hdb.get_helpban_guild(interaction.guild.id)
        if not helpban_list:
            await interaction.send(
                "No one is help banned. But do not fear to lift the mighty ban hammer!"
            )
            return
        message = "**List of users who are help banned:**\n"
        for ban in helpban_list:
            member = interaction.guild.get_member(ban["user_id"])
            banner = interaction.guild.get_member(ban["banner_id"])
            if not member:
                member = await self.bot.fetch_user(ban["user_id"])
            if not banner:
                banner = await self.bot.fetch_user(ban["banner_id"])
            message += f"{member.mention} - Banned by {banner.mention} - Reason: {ban['reason']}\n"
        await interaction.send(message)

    @helpban.subcommand(name="set")
    async def helpban_set(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = None,
    ):
        await interaction.response.defer()
        is_already_banned = await self.bot.hdb.get_helpban_user(
            member.id, interaction.guild.id
        )
        if is_already_banned:
            await interaction.send("This user is already help banned.")
            return
        await self.bot.hdb.set_helpban(
            member.id, interaction.user.id, interaction.guild.id, reason
        )
        await interaction.send(
            f"{member.mention} has been banned from the help system for {reason}."
        )

    @helpban.subcommand(name="remove")
    async def helpban_remove(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        await interaction.response.defer()
        is_already_banned = await self.bot.hdb.get_helpban_user(
            member.id, interaction.guild.id
        )
        if not is_already_banned:
            await interaction.send("This user is not help banned.")
            return
        await self.bot.hdb.remove_helpban(member.id, interaction.guild.id)
        await interaction.send(
            f"{member.mention} has been unbanned from the help system."
        )

    @helpban.subcommand(name="clear")
    async def helpban_clear(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        helpban_list = await self.bot.hdb.get_helpban_guild(interaction.guild.id)
        if not helpban_list:
            await interaction.send(
                "No one is help banned. But do not fear to lift the mighty ban hammer!"
            )
            return
        await self.bot.hdb.clear_helpban(interaction.guild.id)
        await interaction.send("All users have been unbanned from the help system.")

    @commands.Cog.listener(name="on_ready")
    async def persistent_views(self):
        """Adds the persistent views for the help system."""
        open_thread_view = OpenHelpView(self.bot, self.create_help_thread)
        close_thread_view = CloseHelpView(self.close_help_thread, self.is_thread_author)
        if not self.bot.persistent_views_added:
            self.bot.add_view(open_thread_view)
            self.bot.add_view(close_thread_view)
        guild = self.bot.get_guild(config.VIEW_GUILD_ID)
        if not guild:
            raise Exception("View Guild couldn't be found.")
        channel = nextcord.utils.get(guild.channels, id=config.VIEW_CHANNEL_ID)
        if not channel:
            raise Exception("View Channel couldn't be found.")
        await channel.send("Open Thread View", view=open_thread_view)
        await channel.send("Close Thread View", view=close_thread_view)

    @commands.command()
    async def suppress(self, ctx: commands.Context):
        embed = nextcord.Embed(
            description="Successfully suppressed the ping role notification for this help thread.",
            color=EMBED_COLOR,
        )
        await ctx.send(embed=embed, mention_author=False)

    @commands.Cog.listener(name="on_message")
    async def first_message_mention(self, message: nextcord.Message):
        """Mentions the ping role when a user sends their first message in a help thread."""
        if not isinstance(message.channel, nextcord.Thread):
            return
        if message.author.bot:
            return
        guild_config = await self.bot.hdb.get_config(message.guild.id)
        if not guild_config:
            return
        forum_threads = await self.bot.hdb.get_forum_threads(
            guild_config["help_forum_id"]
        )
        thread = next(
            (item for item in forum_threads if item["thread_id"] == message.channel.id),
            None,
        )
        if not thread:
            return
        if not await self.is_thread_author(message.channel.id, message.author.id):
            return
        if thread["has_first_message"]:
            return
        if not message.content.startswith(config.THREAD_MIN_SUPPRESS_PREFIX):
            if len(message.content) < config.THREAD_MIN_CHAR:
                embed = nextcord.Embed(
                    description=config.THREAD_MIN_FAIL, color=EMBED_COLOR
                )
                await message.reply(embed=embed)
                return
            role = nextcord.utils.get(
                message.guild.roles, id=guild_config["ping_role_id"]
            )
            await message.reply(
                role.mention,
                delete_after=2,
                allowed_mentions=nextcord.AllowedMentions(roles=True),
                flags=nextcord.MessageFlags(suppress_notifications=True),
            )
        await self.bot.hdb.set_has_first_message(message.channel.id)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
