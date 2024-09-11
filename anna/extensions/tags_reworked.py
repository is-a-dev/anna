#Copyright (c) 2024 - present, MaskDuck

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

#1. Redistributions of source code must retain the above copyright notice, this
from __future__ import annotations
import uuid
import nextcord
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from nextcord.ext import application_checks, commands

load_dotenv()
import os

# Define the MongoDB setup
class TagEditModal(nextcord.ui.Modal):
    def __init__(self, db, tag_info: dict):
        self._db = db
        self._tag = tag_info
        super().__init__("Edit tag")

        self.my_title = nextcord.ui.TextInput(
            label="Tag Title",
            required=True,
            max_length=60,
            style=nextcord.TextInputStyle.short,
            default_value=self._tag["title"],
        )
        self.add_item(self.my_title)

        self.my_content = nextcord.ui.TextInput(
            label="Tag Content",
            required=True,
            max_length=4000,
            style=nextcord.TextInputStyle.paragraph,
            default_value=self._tag["content"],
        )
        self.add_item(self.my_content)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await self._db.tags.update_one(
            {"_id": self._tag["_id"]},
            {"$set": {"title": self.my_title.value, "content": self.my_content.value}},
        )
        await interaction.response.send_message("Done", ephemeral=True)


class TagEditView(nextcord.ui.View):
    def __init__(self, ctx: commands.Context, db, tag: dict):
        super().__init__()
        self._ctx = ctx
        self._db = db
        self._tag = tag

    @nextcord.ui.button(label="Edit tag!", style=nextcord.ButtonStyle.green)
    async def create_tag(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self._ctx.author.id:
            modal = TagEditModal(self._db, self._tag)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("You cannot edit this tag", ephemeral=True)


class TagCreationModal(nextcord.ui.Modal):
    def __init__(self, db):
        self._db = db
        super().__init__("Create tag")

        self.my_name = nextcord.ui.TextInput(
            label="Tag Name",
            required=True,
            max_length=60,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.my_name)

        self.my_title = nextcord.ui.TextInput(
            label="Tag Title",
            required=True,
            max_length=60,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.my_title)

        self.my_content = nextcord.ui.TextInput(
            label="Tag Content",
            required=True,
            max_length=4000,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.my_content)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        existing_tag = await self._db.tags.find_one({"name": self.my_name.value})
        if not existing_tag:
            tag_id = uuid.uuid4().hex
            await self._db.tags.insert_one({
                "_id": tag_id,
                "name": self.my_name.value,
                "title": self.my_title.value,
                "content": self.my_content.value,
                "author_id": str(interaction.user.id),
            })
            await interaction.response.send_message("Tag created successfully", ephemeral=True)
        else:
            await interaction.response.send_message("Tag already exists", ephemeral=True)


class TagCreationView(nextcord.ui.View):
    def __init__(self, ctx: commands.Context, db):
        super().__init__()
        self._ctx = ctx
        self._db = db

    @nextcord.ui.button(label="Create tag!", style=nextcord.ButtonStyle.green)
    async def create_tag(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self._ctx.author.id:
            modal = TagCreationModal(self._db)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("You cannot create this tag", ephemeral=True)


class TagsNewSlash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot
        # MongoDB connection
        self._db = AsyncIOMotorClient(os.getenv("MONGO")).get_database("anna")

    @nextcord.slash_command()
    async def tag(self, interaction: nextcord.Interaction) -> None:
        pass

    @tag.subcommand()
    @application_checks.has_role(1281898369245253741)
    async def create(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_modal(TagCreationModal(self._db))

    @tag.subcommand()
    @application_checks.has_role(1281898369245253741)
    async def edit(self, interaction: nextcord.Interaction, tag_name: str) -> None:
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            await interaction.response.send_modal(TagEditModal(self._db, tag))
        else:
            await interaction.response.send_message("Tag not found", ephemeral=True)

    @tag.subcommand()
    async def find(self, interaction: nextcord.Interaction, tag_name: str) -> None:
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            embed = nextcord.Embed(title=tag["title"], description=tag["content"], color=nextcord.Color.blue())
            embed.set_footer(text=f"ID: {tag['_id']}, Author: {tag['author_id']}")
            await interaction.send(embed=embed)
        else:
            await interaction.send("Tag not found", ephemeral=True)

    @tag.subcommand()
    async def delete(self, interaction: nextcord.Interaction, tag_name: str) -> None:
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            await self._db.tags.delete_one({"name": tag_name})
            await interaction.send("Tag deleted successfully")
        else:
            await interaction.send("Tag not found")


class TagsNew(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot
        self._db = AsyncIOMotorClient(os.getenv("MONGO")).get_database("anna")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message) -> None:
        if message.content.startswith("^"):
            tag_name = message.content[1:]
            tag = await self._db.tags.find_one({"name": tag_name})
            if tag:
                embed = nextcord.Embed(title=tag["title"], description=tag["content"], color=nextcord.Color.blue())
                embed.set_footer(text=f"ID: {tag['_id']}, Author: {tag['author_id']}")
                await message.channel.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, tag_name: str = "null"):
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            embed = nextcord.Embed(title=tag["title"], description=tag["content"], color=nextcord.Color.blue())
            embed.set_footer(text=f"ID: {tag['_id']}, Author: {tag['author_id']}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Tag not found")

    @tag.command()
    async def list(self, ctx: commands.Context):
        tags = await self._db.tags.find().to_list(length=100)
        tag_names = [tag["name"] for tag in tags]
        await ctx.send(", ".join(tag_names))

    @tag.command()
    @commands.check(lambda ctx: ctx.author.id == 716134528409665586)
    async def create(self, ctx: commands.Context):
        await ctx.send(view=TagCreationView(ctx, self._db))

    @tag.command()
    @commands.check(lambda ctx: ctx.author.id == 716134528409665586)
    async def delete(self, ctx: commands.Context, tag_name: str):
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            await self._db.tags.delete_one({"name": tag_name})
            await ctx.send("Tag deleted")
        else:
            await ctx.send("Tag not found")

    @tag.command()
    @commands.check(lambda ctx: ctx.author.id == 716134528409665586)
    async def edit(self, ctx: commands.Context, tag_name: str):
        tag = await self._db.tags.find_one({"name": tag_name})
        if tag:
            await ctx.send(f"Editing tag {tag_name}", view=TagEditView(ctx, self._db, tag))
        else:
            await ctx.send("Tag not found")


def setup(bot):
    bot.add_cog(TagsNew(bot))
    bot.add_cog(TagsNewSlash(bot))
