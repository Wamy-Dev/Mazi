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

    @app_commands.command(name="search", description="Pesquise um item na sua biblioteca do Plex.")
    @app_commands.describe(search="O item que você deseja pesquisar.", library="Defina a biblioteca Plex da qual você gostaria de hospedar.")
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
                button = discord.ui.Button(label="Vincule sua conta do Discord", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                view = discord.ui.View()
                view.add_item(button)
                embed = discord.Embed(title = "Conta do Discord não vinculada!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie um, se necessário. É necessário vincular sua conta do Discord antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule sua conta do Discord", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Conta do Discord não vinculada!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie um, se necessário. É necessário vincular sua conta do Discord antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex account linked
        try:
            plexstatus = data['plex']
        except:
            button = discord.ui.Button(label="Vincule sua conta do Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Conta Plex não vinculada!", description=f"```❌ Você não tem uma conta Plex vinculada à sua conta Mazi. É necessário Vincular um antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex server linked
        try:
            plexserver = data['plexserver']
            if len(plexserver) == 0:
                button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="Ver exemplo de URLs de servidor", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Plex Server não vinculado!", description=f"```❌ Você não tem uma conta Plex vinculada à sua conta Mazi. É necessário Vincular um antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="Ver exemplo de URLs de servidor", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Plex Server não vinculado!", description=f"```❌ Você não tem um servidor Plex vinculado à sua conta Mazi. Adicione um, pois é necessário para hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
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
                button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="Ver exemplos de nomes de bibliotecas", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ Você não tem uma biblioteca Plex vinculada à sua conta Mazi. Adicione um, pois é necessário para hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return

        except:
            button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="Ver exemplos de nomes de bibliotecas", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ ```", colour = discord.Colour.from_rgb(229,160,13))
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
                    embed = discord.Embed(title = "Nenhum resultado encontrado!", description=f"```❌ Nenhum resultado encontrado na biblioteca: {libraryname} ao pesquisar por {search}. Tente novamente mais tarde ou altere a pesquisa.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed)
                else:
                    embed = discord.Embed(title = f"Principais resultados em {libraryname}", description=movieslist, colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed)
            except Exception as e:
                print(e)
                button = discord.ui.Button(label="Corrigir contas", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="Ver exemplos", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Servidor não acessível!", description=f"```❌ Seu servidor não está acessível. Isso pode ocorrer porque o URL do seu servidor não está acessível ou está errado, ou porque a biblioteca do seu servidor não está correta. Veja os exemplos se precisar de ajuda para adicionar seu link ou biblioteca.```", colour = discord.Colour.from_rgb(229,160,13))
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
