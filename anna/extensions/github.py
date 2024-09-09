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
MERGED_EMOJI_ID = 1249727995174719620
RC_EMOJI_ID = 1282741347303821423

# PR_CHANNEL_ID = 1281898370134183950
# STAFF_ROLE_ID = 1281898369245253741
# MERGED_EMOJI_ID = 1281976493185962086
# RC_EMOJI_ID = 1282269301826654289

class _PRRawObject(object):
    def __init__(self, *, repo_owner: str, repo_name: str, pr_id: str) -> None:
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.pr_id = pr_id

class GitHub(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
                    color = nextcord.Color.purple() if merged else nextcord.Color.blue()

                    # Embed description for the PR/issue
                    embed_description += f"[(#{pr.pr_id}) {i['title']}]({i['html_url']})\n"

                    # Build and send the embed
                    embed = nextcord.Embed(
                        title=f"PR/Issue: {pr.repo_name}",
                        description=embed_description,
                        color=color,
                    )
                    await message.channel.send(embed=embed)

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
    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if reaction.message.channel.id == PR_CHANNEL_ID and reaction.emoji.id == MERGED_EMOJI_ID:
            # Check if the user has the staff role
            if STAFF_ROLE_ID in [role.id for role in user.roles]:
                embed = reaction.message.embeds[0]  # Get the original embed

                # Update the embed
                embed.clear_fields()
                embed.add_field(name="Status", value="Merged", inline=True)
                embed.color = nextcord.Color.purple()  # Change color to purple

                # Edit the message with the updated embed
                await reaction.message.edit(embed=embed)
        if reaction.message.channel.id == PR_CHANNEL_ID and reaction.emoji.id == RC_EMOJI_ID:
            # Check if the user has the staff role
            if STAFF_ROLE_ID in [role.id for role in user.roles]:
                embed = reaction.message.embeds[0]  # Get the original embed

                # Update the embed
                embed.clear_fields()
                embed.add_field(name="Status", value="Requested changes / closed", inline=True)
                embed.color = nextcord.Color.red()  # Change color to purple

                # Edit the message with the updated embed
                await reaction.message.edit(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GitHub(bot))
