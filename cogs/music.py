import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import enum
import urllib.parse
import base64
from main import config_items

bigDict = {
    "convertsonglink": {
        "name": "convertsonglink",
        "description": "Using song.link API, convert a song from one platform to another. `all` if a platform is not found",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "searchspotify": {
        "name": "searchspotify",
        "description": "Searches Spotify for a song and gives it for the wanted platform. If not Spotify, uses song.link API",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
}

class music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree

    class musicStreamingServices(enum.Enum):
        all = "all"
        Amazon_Music = "amazonMusic"
        Amazon_Store = "amazonStore"
        Anghami = "anghami"
        Apple_Music = "appleMusic"
        Audiomack = "audiomack"
        Audius = "audius"
        Boomplay = "boomplay"
        Deezer = "deezer"
        Google = "google"
        Google_Store = "googleStore"
        iTunes = "itunes"
        Napster = "napster"
        Pandora = "pandora"
        Soundcloud = "soundcloud"
        Spinrilla = "spinrilla"
        Spotify = "spotify"
        Tidal = "tidal"
        Yandex = "yandex"
        Youtube = "youtube"
        Youtube_Music = "youtubeMusic"

    class OpenInAppView(discord.ui.View):
        def __init__(self, platform: str, song_url: str, song: str = "", artist: str = ""):
            super().__init__(timeout=300)  # 5 minute timeout
            self.platform = platform
            self.song_url = song_url
            # self.song = song
            # self.artist = artist
            
            """
            if platform == "appleMusic":
                app_url = f"music://{song_url.split('https://')[1]}"
                self.add_item(
                    discord.ui.Button(
                        label="Open in Apple Music App",
                        url=app_url,
                        style=discord.ButtonStyle.link,
                        emoji="🎵"
                    )
                )
            """
            self.add_item(
                discord.ui.Button(
                    label="Fancy button for you to press",
                    url=song_url,
                    style=discord.ButtonStyle.link,
                    emoji="🤰"
                )
            )


    @app_commands.describe(
        link="The link to the song", 
        converttoplatform="The platform to convert the link to. Use 'all' to get links for all platforms", 
        issingle="Set to True if the song is a single (the only song in an album)"
    )
    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["convertsonglink"])
    async def convertsonglink(self, interaction: discord.Interaction, link: str, converttoplatform: musicStreamingServices, issingle: bool = False):
        await interaction.response.defer()

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.song.link/v1-alpha.1/links?url={urllib.parse.quote(link)}&songIfSingle={str(issingle).lower()}") as response:
                data = await response.json()
        try:
            if data["statusCode"] == 400:
                if data["code"] == "could_not_resolve_entity":
                    await interaction.followup.send("Invalid link. Profile links are not supported by song.link.", ephemeral=True)
                    return
                elif data["code"] == "could_not_fetch_entity_data":
                    await interaction.followup.send("Invalid link. The link provided is not a valid song link.", ephemeral=True)
                    return
                else:
                    await interaction.followup.send("An error occurred: " + data["code"], ephemeral=True)
                    return
        except KeyError:
            pass
        SongID = data["entityUniqueId"]
        song = data["entitiesByUniqueId"][SongID]["title"]
        artist = data["entitiesByUniqueId"][SongID]["artistName"]

        if converttoplatform == self.musicStreamingServices.all:
            await interaction.followup.send(f"all music players for {song} by {artist}: {data["pageUrl"]}")
            return
        else:
            selected_platform = converttoplatform.value
            try:
                song_url = data["linksByPlatform"][selected_platform]["url"]
            except KeyError:
                await interaction.followup.send(f"Could not find a link for {selected_platform.capitalize()}, defaulting to all platforms:\n*{song}* by {artist}: {data["pageUrl"]}")
                return
            view = self.OpenInAppView(selected_platform, song_url) # Unfortunately, only http(s)/discord is supported :/
            await interaction.followup.send(f"*{song}* by {artist}:\n{song_url}", view=view)


    @app_commands.describe(
        songname="Name of the song to find",
        songartist="Artist of the song to find",
        converttoplatform="The platform to convert the link to. Use 'all' to get links for all platforms"
    )
    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["searchspotify"])
    async def searchspotify(self, interaction: discord.Interaction, songname: str, songartist: str, converttoplatform: musicStreamingServices):
        await interaction.response.defer()
        song = songname.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~").replace("`", "\\`")
        artist = songartist.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~").replace("`", "\\`")

        # get access token
        spotifyClientID = config_items["spotify"]["spotifyClientID"]
        spotifyClientSecret = config_items["spotify"]["spotifyClientSecret"]
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                headers={
                    "Authorization": "Basic " + base64.b64encode(f"{spotifyClientID}:{spotifyClientSecret}".encode()).decode(),
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            ) as response:
                response = await response.json()
        spotifyAccessToken: str = response["access_token"]

        # get song data
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.spotify.com/v1/search?q={song}%20artist:{artist}&type=track&limit=1",
                headers={"Authorization": f"Bearer {spotifyAccessToken}"}
            ) as spotify_track_data:
                spotify_track_data = await spotify_track_data.json()
        try:
            spotifySongID = spotify_track_data["tracks"]["items"][0]["id"]
        except IndexError:
            await interaction.followup.send("Could not find the song on Spotify via search.", ephemeral=True)
            return
        
        if converttoplatform == self.musicStreamingServices.Spotify:
            spotifySongURL = spotify_track_data["tracks"]["items"][0]["external_urls"]["spotify"]
            spotifySongName = spotify_track_data["tracks"]["items"][0]["name"]
            spotifySongArtist = spotify_track_data["tracks"]["items"][0]["artists"][0]["name"]
            await interaction.followup.send(f"*{spotifySongName}* by {spotifySongArtist}:\n{spotifySongURL}") # Don't wanna use the song.link API more than needed :3
            return

        # get song link
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.song.link/v1-alpha.1/links?platform=spotify&type=song&id={spotifySongID}"
            ) as response:
                data = await response.json()


        if converttoplatform == self.musicStreamingServices.all:
            await interaction.followup.send(f"all music players for {song} by {artist}: {data["pageUrl"]}")
            return
        else:
            selected_platform = converttoplatform.value
            try:
                song_url = data["linksByPlatform"][selected_platform]["url"]
            except KeyError:
                await interaction.followup.send(f"Could not find a link for {selected_platform.capitalize()}, defaulting to all platforms:\n*{song}* by {artist}: {data["pageUrl"]}")
                return
            await interaction.followup.send(f"*{song}* by {artist}:\n{song_url}")

async def setup(bot: commands.Bot):
    await bot.add_cog(music(bot))