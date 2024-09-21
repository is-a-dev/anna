import aiohttp
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption

# Helper function for API requests
async def request(url, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request('GET', url, *args, **kwargs) as response:
            return await response.json()

class MAL_Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def anime(self, ctx: commands.Context, *, anime_name: str):
        """Command for searching anime on MyAnimeList. Usage example: `a?anime Lycoris Recoil"""
        url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        try:
            data = await request(url)
            if data and data.get("data"):
                anime = data["data"][0]
                title = anime.get("title", "N/A")
                episodes = anime.get("episodes", "N/A")
                score = anime.get("score", "N/A")
                status = anime.get("status", "N/A")
                airing = anime.get("airing", "N/A")
                type = anime.get("type", "N/A")
                duration = anime.get("duration", "N/A")
                rating = anime.get("rating", "N/A")
                cover_image = anime["images"]["jpg"]["image_url"]
                url = anime.get("url", "N/A")
                genres = ", ".join([genre['name'] for genre in anime.get("genres", [])])

                embed = nextcord.Embed(title=title, url=url, color=nextcord.Color.blue())
                embed.add_field(name="Episodes", value=episodes, inline=True)
                embed.add_field(name="Score", value=score, inline=True)
                embed.add_field(name="Status", value=status, inline=True)
                embed.add_field(name="Airing", value=airing, inline=True)
                embed.add_field(name="Type", value=type, inline=True)
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.set_thumbnail(url=cover_image)
                embed.set_footer(text=f"Genres: {genres}")

            else:
                embed = nextcord.Embed(title="Anime not found.", color=nextcord.Color.blue())

        except Exception as e:
            embed = nextcord.Embed(title="Error", description=str(e), color=nextcord.Color.blue())
        if rating == "Rx - Hentai":
            await ctx.send("Searching for anime rated Rx has been disabled.")
        else:
            await ctx.send(embed=embed)

    @nextcord.slash_command(name="anime", description="Get information about an anime")
    async def slash_anime(
        self,
        interaction: Interaction,
        anime_name: str = SlashOption(description="Name of the anime")
    ):
        """Slash command for searching anime on MyAnimeList. Usage example: `/anime anime_name:Lycoris Recoil"""
        url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        try:
            data = await request(url)
            if data and data.get("data"):
                anime = data["data"][0]
                title = anime.get("title", "N/A")
                episodes = anime.get("episodes", "N/A")
                score = anime.get("score", "N/A")
                status = anime.get("status", "N/A")
                airing = anime.get("airing", "N/A")
                type = anime.get("type", "N/A")
                duration = anime.get("duration", "N/A")
                rating = anime.get("rating", "N/A")
                cover_image = anime["images"]["jpg"]["image_url"]
                url = anime.get("url", "N/A")
                genres = ", ".join([genre['name'] for genre in anime.get("genres", [])])

                embed = nextcord.Embed(title=title, url=url, color=nextcord.Color.blue())
                embed.add_field(name="Episodes", value=episodes, inline=True)
                embed.add_field(name="Score", value=score, inline=True)
                embed.add_field(name="Status", value=status, inline=True)
                embed.add_field(name="Airing", value=airing, inline=True)
                embed.add_field(name="Type", value=type, inline=True)
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.set_thumbnail(url=cover_image)
                embed.set_footer(text=f"Genres: {genres}")

            else:
                embed = nextcord.Embed(title="Anime not found.", color=nextcord.Color.blue())

        except Exception as e:
            embed = nextcord.Embed(title="Error", description=str(e), color=nextcord.Color.blue())
        if rating == "Rx - Hentai":
            await interaction.response.send_message("Searching for anime rated Rx has been disabled.")
        else:
            await interaction.response.send_message(embed=embed)

class MAL_Manga(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def manga(self, ctx: commands.Context, *, manga_name: str):
        """Command for searching manga on MyAnimeList. Usage example: `a?manga Shikanoko Nokonoko Koshitantan"""
        url = f"https://api.jikan.moe/v4/manga?q={manga_name}&limit=1"
        try:
            data = await request(url)
            if data and data.get("data"):
                manga = data["data"][0]
                title = manga.get("title", "N/A")
                chapters = manga.get("chapters", "N/A")
                score = manga.get("score", "N/A")
                status = manga.get("status", "N/A")
                cover_image = manga["images"]["jpg"]["image_url"]
                url = manga.get("url", "N/A")
                genres = ", ".join([genre['name'] for genre in manga.get("genres", [])])

                embed = nextcord.Embed(title=title, url=url, color=nextcord.Color.blue())
                embed.add_field(name="Chapters", value=chapters, inline=True)
                embed.add_field(name="Score", value=score, inline=True)
                embed.add_field(name="Status", value=status, inline=True)
                embed.set_thumbnail(url=cover_image)
                embed.set_footer(text=f"Genres: {genres}")

            else:
                embed = nextcord.Embed(title="Manga not found.", color=nextcord.Color.blue())

        except Exception as e:
            embed = nextcord.Embed(title="Error", description=str(e), color=nextcord.Color.blue())
        await ctx.send(embed=embed)

    @nextcord.slash_command(name="manga", description="Get information about a manga")
    async def slash_manga(
        self,
        interaction: Interaction,
        manga_name: str = SlashOption(description="Name of the manga")
    ):
        """Slash command for searching manga on MyAnimeList. Usage example: `/manga manga_name:Shikanoko Nokonoko Koshitantan"""
        url = f"https://api.jikan.moe/v4/manga?q={manga_name}&limit=1"
        try:
            data = await request(url)
            if data and data.get("data"):
                manga = data["data"][0]
                title = manga.get("title", "N/A")
                chapters = manga.get("chapters", "N/A")
                score = manga.get("score", "N/A")
                status = manga.get("status", "N/A")
                cover_image = manga["images"]["jpg"]["image_url"]
                url = manga.get("url", "N/A")
                genres = ", ".join([genre['name'] for genre in manga.get("genres", [])])

                embed = nextcord.Embed(title=title, url=url, color=nextcord.Color.blue())
                embed.add_field(name="Chapters", value=chapters, inline=True)
                embed.add_field(name="Score", value=score, inline=True)
                embed.add_field(name="Status", value=status, inline=True)
                embed.set_thumbnail(url=cover_image)
                embed.set_footer(text=f"Genres: {genres}")

            else:
                embed = nextcord.Embed(title="Manga not found.", color=nextcord.Color.blue())

        except Exception as e:
            embed = nextcord.Embed(title="Error", description=str(e), color=nextcord.Color.blue())
        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(MAL_Anime(bot))
    bot.add_cog(MAL_Manga(bot))
