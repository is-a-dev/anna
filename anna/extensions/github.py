from __future__ import annotations
import re
from typing import List
import aiohttp
import nextcord
from nextcord.ext import commands

# GitHub request helper
async def request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(*args, **kwargs) as ans:
            return await ans.json()

# Regex patterns
FULL_MATCH_ANY_REPO = r"(https:\/\/github.com\/)?([A-Za-z1-9-]+)\/([A-Za-z1-9-]+)(\/pull)?(#|\/)(?P<pr_id>\d+)"
VERY_SHORT_MESSAGE = r"##(\d+)"
PR_CHANNEL_ID = 1130858271620726784
STAFF_ROLE_ID = 1197475623745110109

class _PRRawObject(object):
    def __init__(self, *, repo_owner: str, repo_name: str, pr_id: str) -> None:
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_id = pr_id

class GitHub(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.message_pr_map = {}  # To keep track of PR message IDs and their details

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Match for repo format 'repo:owner/repo'
        repo_matches: List[re.Match] = re.findall(r"repo:([A-Za-z1-9-]+)/([A-Za-z1-9-]+)", message.content)
        full_matches: List[re.Match] = re.findall(FULL_MATCH_ANY_REPO, message.content)
        very_short_matches: List[re.Match] = re.findall(VERY_SHORT_MESSAGE, message.content)

        pr_list: List[_PRRawObject] = []
        embed_description = ""  # For final description aggregation

        # Handle PRs/issues from full matches (links or #)
        if len(full_matches) > 0:
            for x in full_matches:
                if x[0] == "https://github.com/":
                    await message.edit(suppress=True)
                repo_owner = x[1]
                repo_name = x[2]
                pr_id = x[5]
                pr_list.append(
                    _PRRawObject(
                        repo_owner=repo_owner, repo_name=repo_name, pr_id=pr_id
                    )
                )

        # Handle very short messages (##PRNUMBER) as is-a-dev/register
        if len(very_short_matches) > 0:
            for pr_id in very_short_matches:
                pr_list.append(
                    _PRRawObject(
                        repo_owner="is-a-dev",
                        repo_name="register",
                        pr_id=pr_id
                    )
                )

        # Only process PR/issue embed once for all PRs/issues
        if len(pr_list) > 0:
            for pr in pr_list:
                try:
                    i = await request(
                        "GET",
                        f"https://api.github.com/repos/{pr.repo_owner}/{pr.repo_name}/issues/{pr.pr_id}",
                    )

                    # Check if the PR is open, closed, or merged
                    state = i.get('state', 'open')
                    merged = i.get('merged', False)

                    # Color based on state
                    color = nextcord.Color.blue()  # Default to open

                    # Embed description for the PR/issue
                    embed_description += f"[(#{pr.pr_id}) {i['title']}]({i['html_url']})\n"

                    # Build and send the embed
                    embed = nextcord.Embed(
                        title=f"PR/Issue: {pr.repo_name}",
                        description=embed_description,
                        color=color,
                    )
                    # embed.add_field(name="Status", value=state.title(), inline=True)
                    sent_message = await message.channel.send(embed=embed)

                    # Track the message ID and associated PR information
                    if pr.repo_owner == "is-a-dev" and pr.repo_name == "register":
                        self.message_pr_map[sent_message.id] = pr

                except aiohttp.ClientError as e:
                    embed_description += f"Error fetching PR #{pr.pr_id}: {str(e)}\n"

            return  # Prevent sending another embed below
        
        if len(pr_list) == 0:
            if message.channel.id == PR_CHANNEL_ID:
                if message.author.get_role(STAFF_ROLE_ID) is None:  # type: ignore
                    await message.delete()

            return
        
        # Handle repo:owner/repo matches
        if len(repo_matches) > 0:
            for repo_owner, repo_name in repo_matches:
                try:
                    repo_info = await request(
                        "GET", f"https://api.github.com/repos/{repo_owner}/{repo_name}"
                    )
                    owner_info = await request(
                        "GET", f"https://api.github.com/users/{repo_owner}"
                    )

                    # Owner profile image and other details
                    owner_name = owner_info.get("login", "Unknown")
                    owner_avatar = owner_info.get("avatar_url", "")

                    # Repository details
                    repo_url = repo_info.get("html_url", f"https://github.com/{repo_owner}/{repo_name}")
                    repo_description = repo_info.get("description", "No description available")
                    stars = repo_info.get("stargazers_count", 0)
                    forks = repo_info.get("forks_count", 0)

                    # Check for social preview image (as a "banner")
                    repo_banner = repo_info.get("social_preview_url", "")
                    topics = repo_info.get("topics", [])

                    # Embedding repository information
                    embed = nextcord.Embed(
                        title=f"Repository: {repo_owner}/{repo_name}",
                        description=f"[Visit Repository]({repo_url})\n{repo_description}",
                        color=nextcord.Color.blue(),
                    )
                    embed.set_thumbnail(url=owner_avatar)
                    embed.add_field(name="Stars", value=str(stars), inline=True)
                    embed.add_field(name="Forks", value=str(forks), inline=True)

                    if topics:
                        embed.add_field(name="Topics", value=", ".join(topics), inline=False)

                    # Add repository banner if available
                    if repo_banner:
                        embed.set_image(url=repo_banner)

                    await message.channel.send(embed=embed)
                except aiohttp.ClientError as e:
                    await message.channel.send(f"Error fetching repository {repo_owner}/{repo_name}: {str(e)}")
                    continue

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.User):
        if reaction.message.channel.id != PR_CHANNEL_ID:
            return

        if reaction.emoji != '✅':  # Assuming you use '✅' to mark a PR as merged
            return

        if reaction.message.id not in self.message_pr_map:
            return

        pr = self.message_pr_map[reaction.message.id]

        # Check if the user has the STAFF_ROLE_ID
        member = reaction.message.guild.get_member(user.id)
        if member is None or STAFF_ROLE_ID not in [role.id for role in member.roles]:
            return

        # Fetch the current embed
        embed = reaction.message.embeds[0] if reaction.message.embeds else None
        if embed is None:
            return

        # Create a new embed with updated color and field
        new_embed = nextcord.Embed.from_dict(embed.to_dict())
        new_embed.color = nextcord.Color.purple()  # Change to purple for merged
        new_embed.add_field(name="Status", value="Merged", inline=True)

        # Edit the message with the new embed
        await reaction.message.edit(embed=new_embed)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(GitHub())
