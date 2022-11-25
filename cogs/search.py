import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands
from firebase_admin import firestore
from decouple import config
from nacl.secret import SecretBox
from plexapi.server import PlexServer
import requests
import urllib3
from base64 import b64decode

db = firestore.client()
session = requests.Session()
session.verify = False
urllib3.disable_warnings()

class Search(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="search", description="Search for an item in your Plex library.")
    @app_commands.describe(search="The item you want to search for.", library="Define the Plex library you would like to host from.")
    async def search(self, interaction: Interaction, search: str, library: str = None):
        await interaction.response.defer() #wait until the bot is finished thinking
        discordid = interaction.user.id
        # First check if the user is in the database
        try:
            docs = db.collection(u'userdata').where(u'discordid', u'==', discordid).stream()
            empty = True
            for doc in docs:
                empty = False
                data = doc.to_dict()
            if empty:
                button = discord.ui.Button(label="Link your Discord account", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                view = discord.ui.View()
                view.add_item(button)
                embed = discord.Embed(title = "Discord account not linked!", description=f"```❌ You don't have a Discord account linked to your Mazi account. You also may not have a Mazi account. Please create one if needed. Please link your Discord account before using any features as it is required.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Link your Discord account", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Discord account not linked!", description=f"```❌ You don't have a Discord account linked to your Mazi account. You also may not have a Mazi account. Please create one if needed. Please link your Discord account before using any features as it is required.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex account linked
        try:
            plexstatus = data['plex']
        except:
            button = discord.ui.Button(label="Link your Plex account", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Plex account not linked!", description=f"```❌ You don't have a Plex account linked to your Mazi account. Please link one before using any features as it is required.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex server linked
        try:
            plexserver = data['plexserver']
            if len(plexserver) == 0:
                button = discord.ui.Button(label="Link your Plex server", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="View example server URLS", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Plex Server not linked!", description=f"```❌ You don't have a Plex server linked to your Mazi account. Please add one as it is required to host sessions.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Link your Plex server", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="View example server URLS", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Plex Server not linked!", description=f"```❌ You don't have a Plex server linked to your Mazi account. Please add one as it is required to host sessions.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex library linked
        try:
            if library == None:
                plexlibrary = data['plexlibrary']
            else:
                plexlibrary = library
            if len(plexlibrary) == 0:
                button = discord.ui.Button(label="Link your Plex server", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="View example library names", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Plex Library not linked!", description=f"```❌ You don't have a Plex library linked to your Mazi account. Please add one as it is required to host sessions.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return

        except:
            button = discord.ui.Button(label="Link your Plex server", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="View example library names", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Plex Library not linked!", description=f"```❌ You don't have a Plex library linked to your Mazi account. Please add one as it is required to host sessions.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return

        if plexstatus and plexserver and plexlibrary:
            if library == None:
                libraryname = data["plexlibrary"]
            else:
                libraryname = library
            try:
                moviefields = []
                for movie in searchPlex(data, search, libraryname):
                    moviefields.append(movie)
                movieslist = ""
                for items in moviefields:
                    movieslist += f'{items}\n'
                if len(moviefields) == 0:
                    embed = discord.Embed(title = "No results found!", description=f"```❌ No results found in library: {libraryname} when searching for {search}. Please try again later or change search.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed)
                else:
                    embed = discord.Embed(title = f"Top results in {libraryname}", description=movieslist, colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed)
            except Exception as e:
                print(e)
                button = discord.ui.Button(label="Fix accounts", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="View examples", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Server not accessible!", description=f"```❌ Your sever is not accessible. This could be due to your server url being not accessible or wrong, or to your server library not being correct. Please view the examples if you need help adding your link or library.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                await interaction.followup.send(embed = embed, view=view)
                return

def searchPlex(data, title, libraryname):
    try:
        encrypted = b64decode(data["plexauth"].encode("utf-8"))
        secret_key = config('AESKEY')
        box = SecretBox(bytes(secret_key, encoding='utf8'))
        plexauth = box.decrypt(encrypted).decode("utf-8")
        plexurl = data["plexserver"]
        if not (plexurl.startswith('http') or plexurl.startswith('https')):
            try:
                plexurl = f'http://{plexurl}'
                plex = PlexServer(plexurl, plexauth, session=session)
            except:
                plexurl = f'https://{plexurl}'
                plex = PlexServer(plexurl, plexauth, session=session)
        else:
            plex = PlexServer(plexurl, plexauth, session=session)
        movies = plex.library.section(libraryname)
    except Exception as e:
        print(e)
        return None
    list = []
    for video in movies.search(title = title, maxresults = 5):
        list.append(video.title)
    return(list)

async def setup(client):
    await client.add_cog(Search(client))