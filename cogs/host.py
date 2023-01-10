import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands
from firebase_admin import firestore
from decouple import config
from base64 import b64decode
from nacl.secret import SecretBox
from plexapi.server import PlexServer
import requests
import urllib3
import random
import asyncio

db = firestore.client()
countsdoc = db.collection(u'counts').document(u'counts')
session = requests.Session()
session.verify = False
urllib3.disable_warnings()

class Host(commands.Cog):

    def __init__(self, client):
        self.client = client
    @app_commands.command(name="host", description="Hospede uma exibição de filme (Assistir Juntos) com seus amigos.")
    @app_commands.describe(library="Defina a biblioteca Plex que você gostaria de hospedar.", moviechoice = "descubra o título exato do filme que você deseja assistir. Use /movies ou /search para obter o título.", timetostart = "O tempo em minutos para seus amigos participarem da sessão de Assistir Juntos. (Predefinição: 5 minutos)")
    async def host(self, interaction: Interaction, moviechoice: str, timetostart: int = 5, library: str = None):
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
                embed = discord.Embed(title = "Conta do Discord não vinculada!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie uma, se necessário. É necessário Vincular antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule sua conta do Discord", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Conta do Discord não vinculada!", description=f"```❌ Você não tem uma conta Discord vinculada à sua conta Mazi. Você também pode não ter uma conta Mazi. Por favor, crie um, se necessário. É necessário Vincular antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex account linked
        try:
            plexstatus = data['plex']
        except:
            button = discord.ui.Button(label="Vincule sua conta do Plex!", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            view = discord.ui.View()
            view.add_item(button)
            embed = discord.Embed(title = "Biblioteca Plex não vinculada!!", description=f"```❌ Você não tem uma conta Plex vinculada à sua conta Mazi. , É necessário Vincular antes de usar qualquer recurso.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex server linked
        try:
            plexserver = data['plexserver']
            if len(plexserver) == 0:
                button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
                button2 = discord.ui.Button(label="Ver URLs de exemplo de servidor", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Plex Server não vinculado!", description=f"```❌ Você não tem um servidor Plex vinculado à sua conta Mazi. É necessário Vincular antes de hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="Ver URLs de servidor de exemplo", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ Você não tem um servidor Plex vinculado à sua conta Mazi. É necessário Vincular antes de hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
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
                button2 = discord.ui.Button(label="Ver URLs de servidor de exemplo", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
                view = discord.ui.View()
                view.add_item(button)
                view.add_item(button2)
                embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ Você não tem uma biblioteca Plex vinculada à sua conta Mazi. É necessário Vincular antes de hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                await interaction.followup.send(embed=embed, view=view)
                return
        except:
            button = discord.ui.Button(label="Vincule seu servidor Plex", style=discord.ButtonStyle.link, url="https://mazi.pw/user")
            button2 = discord.ui.Button(label="Ver exemplos de nomes de bibliotecas", style=discord.ButtonStyle.link, url="https://github.com/Wamy-Dev/Mazi/wiki/Examples")
            view = discord.ui.View()
            view.add_item(button)
            view.add_item(button2)
            embed = discord.Embed(title = "Biblioteca Plex não vinculada!", description=f"```❌ Você não tem uma biblioteca Plex vinculada à sua conta Mazi. É necessário Vincular antes de hospedar sessões.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        if plexstatus and plexserver and plexlibrary:
            if library == None:
                libraryname = data["plexlibrary"]
            else:
                libraryname = library
            try:
                if getHosting(data, moviechoice, libraryname) is None:
                    embed = discord.Embed(title = "Item não encontrado!", description=f"```❌ {moviechoice} não pode ser encontrado na biblioteca: {libraryname}. Por favor, tente novamente.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed=embed)
                    return
                else:
                    token, machineid, movie, key, plex = getHosting(data, moviechoice, libraryname)
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
            try:
                # create room
                counts = countsdoc.get()
                previouscount = counts.to_dict()
                roomnames = ["Ação", "Animação", "Horror", "Aventura", "Comédia", "Romance", "Ficção Científica", "Fantasia", "Musical"]
                roomname = random.choice(roomnames)+"-"+str(previouscount["counts"])
                msg = await interaction.followup.send(f"```Junte-se a este tópico para participar da sessão Watch Together: {roomname}.```")
                thread = await interaction.channel.create_thread(name=f"Assistir Sessão Juntos: {roomname}", message=msg, reason="Mazi criou a sala Watch Together.", auto_archive_duration=60)
                await thread.send("```Para participar, execute '/join' neste tópico.```")
                doc = db.collection(u'counts').document(u'counts')
                userid = data["plexid"]
                thumb = data["plexthumb"]
                title = data["plextitle"]
                email = data["plexemail"]
                channel = thread.id
                discordid = discordid
                # add to database
                ref = db.collection(u'rooms').document(roomname)
                ref.set({
                    u'Hora Iniciada': firestore.SERVER_TIMESTAMP,
                    u'Thread': channel,
                    u'MovieKey': key,
                    u'Server': plexserver,
                    u'MachineID': machineid,
                }, merge=True)
                #now add first user
                userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(str(discordid))
                userref.set({
                    u'id': userid,
                    u'thumb': thumb,
                    u'title': title,
                    u'email': email,
                    }, merge=True)
                #send message that the room is ready
                embed = discord.Embed(title = f"{roomname} agora está aberto para participar!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                embed.add_field(name = f'{libraryname}', value=f"Nós estamos observando {movie.title}!", inline = False)
                embed.add_field(name = 'Join Now', value="A sala já está aberta para participar! Execute /join para participar. Certifique-se de ter vinculado suas contas Plex e Discord.", inline = False)
                if timetostart == 0:
                    embed.set_footer(text = "A entrada na sala não será desativada. O filme começará imediatamente. Isso significa que ninguém poderá entrar.")
                else:
                    embed.set_footer(text = f"A junção da sala fecha em {timetostart} minutos.")
                await thread.send(embed = embed)
            except Exception as e:
                print(e)
                print("erro ao criar sala")
                return
            # update counts
            try:
                doc = db.collection(u'counts').document(u'counts')
                counts = doc.get()
                previouscount = counts.to_dict()
                newcount = int(previouscount['counts']) + 1
                doc.update({u'counts': newcount})
            except Exception as e: 
                print(e)
                print('Falha ao adicionar contagem')
            # timer for room
            await asyncio.sleep(timetostart*60)
            #start room
            try:
                #get users from room
                ref = db.collection(u'rooms').document(roomname)
                doc = ref.get()
                data = doc.to_dict()
                machineid = data["MachineID"]
                moviekey = data["MovieKey"]
                #for users in data get user objects and add them to users
                users = []
                collections = db.collection(u'rooms').document(roomname).collections()
                for collection in collections:
                    for doc in collection.stream():
                        data = doc.to_dict()
                        #send request to all users in rooms
                        username = data["email"]
                        try:
                            plex.myPlexAccount().inviteFriend(user=username, server=plex)
                        except Exception as e:
                            print(e)
                        data.pop("email")
                        users.append(data)
                url = f"https://together.plex.tv/rooms?X-Plex-Token={token}"
                obj = {
                        "sourceUri": f"server://{machineid}/com.plexapp.plugins.library/library/metadata/{moviekey}",
                        "title": movie.title,
                        "users": users
                    }
                try:
                    if timetostart == 0:
                        requests.post(url, json = obj)
                    else:
                        db.collection(u'rooms').document(roomname).delete()
                        await thread.send(f"```Juntando-se para {roomname} está fechado. Abra o Plex em qualquer dispositivo e aceite a solicitação de amizade se você ainda não for amigo do hoster. Então, em 5 minutos, participe da sessão Assistir Juntos. {movie.title.capitalize()} começará em breve.```")
                        await asyncio.sleep(timetostart*60)
                        requests.post(url, json = obj)
                    await thread.send(f"```{roomname} agora começou a assistir {movie.title}!```")
                except:
                    embed = discord.Embed(title = "Servidor não acessível!", description=f"```❌ Algo deu errado e não foi possível arrumar uma sala. Tente novamente mais tarde ou relate isso como um erro usando /project.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed, view=view)
                    return
            except: 
                embed = discord.Embed(title = "Servidor não acessível!", description=f"```❌ Algo deu errado e não foi possível arrumar uma sala. Tente novamente mais tarde ou relate isso como um erro usando /project.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                await interaction.followup.send(embed = embed, view=view)
                return
def getHosting(data, moviechoice, libraryname):
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
        token = plex._token
        machineid = plex.machineIdentifier
        movie = plex.library.section(libraryname).get(moviechoice)
        key = movie.ratingKey
        return token, machineid, movie, key, plex
    except:
        return None

async def setup(client):
    await client.add_cog(Host(client))
