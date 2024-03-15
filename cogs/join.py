import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands
from firebase_admin import firestore
import requests
import urllib3

db = firestore.client()
session = requests.Session()
session.verify = False
urllib3.disable_warnings()

class Join(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="join", description="Junte-se a uma sala de sessão ativa do Plex Assistir Juntos.")
    async def search(self, interaction: Interaction):
        await interaction.response.defer() #wait until the bot is finished thinking
        discordid = interaction.user.id
        channel = interaction.channel.id
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
                embed = discord.Embed(title = "Vincule sua conta do Discord!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie um, se necessário. É necessário vincular sua conta do Discord antes de usar qualquer recurso!.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule sua conta do Discord", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Conta do Discord não vinculada!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie um, se necessário. É necessário vincular sua conta do Discord antes de usar qualquer recurso!.```", colour = discord.Colour.from_rgb(229,160,13))
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
            embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ Você não tem uma conta Plex vinculada à sua conta Mazi. É necessário vincular sua conta do Discord antes de usar qualquer recurso!```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        if plexstatus:
            try:
                docs = db.collection(u'rooms').where(u'Thread', u'==', channel).stream()
                norooms = True
                for rooms in docs:
                    norooms = False
                    roomname = rooms.id
                if norooms:
                    embed = discord.Embed(title = "Não há salas para entrar!", description=f"```❌ Não foram encontradas salas para entrar. Tente novamente mais tarde ou em outro tópico.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    await interaction.followup.send(embed=embed)
                    return
            except:
                embed = discord.Embed(title = "Não há salas que podem ser unidas!", description=f"```❌ Não foram encontradas salas para entrar. Tente novamente mais tarde ou em outro tópico.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed)
                return
            try:
                document = db.collection(u'userdata').where(u'discordid', u'==', discordid).stream()
                empty = True
                for doc in document:
                    empty = False
                    data = doc.to_dict()
                    userid = data["plexid"]
                    thumb = data["plexthumb"]
                    title = data["plextitle"]
                    email = data["plexemail"]
                    #add to roomname
                    userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(str(discordid))
                    userref.set({
                        u'id': userid,
                        u'thumb': thumb,
                        u'title': title,
                        u'email': email
                        }, merge=True)
                    #announce user join
                    embed = discord.Embed(title = f"{interaction.user.display_name} Juntou se a {roomname}!", description=f"```{interaction.user.display_name} receberá um convite para {roomname}.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    await interaction.followup.send(embed=embed)
                if empty:
                    embed = discord.Embed(title = "Erro ao entrar na sala!", description=f"```❌ Erro ao entrar na sala. Tente novamente mais tarde ou reporte este erro usando /project.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    await interaction.followup.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title = "Erro ao entrar na sala!", description=f"```❌ Erro ao entrar na sala. Tente novamente mais tarde ou reporte este erro usando /project.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed)

async def setup(client):
    await client.add_cog(Join(client))
