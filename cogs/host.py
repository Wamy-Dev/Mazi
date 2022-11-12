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

    @app_commands.command(name="host", description="Host a Plex movie watch together with your friends.")
    @app_commands.describe(moviechoice = "The exact title of the movie you want to watch. Use /movies or /search to get the title.", timetostart = "The time in minutes to give your friends to join the watch together session. (Default: 5 minutes)")
    async def host(self, interaction: Interaction, moviechoice: str, timetostart: int = 5):
        await interaction.response.defer() #wait until the bot is finished thinking
        discordid = str(interaction.user.id)
        # First check if the user is in the database
        try:
            docs = db.collection(u'users').where(u'discordid', u'==', discordid).stream()
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
            embed = discord.Embed(title = "Plex Library not linked!", description=f"```❌ You don't have a Plex account linked to your Mazi account. Please link one before using any features as it is required.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
        # Check if the user has a Plex server linked
        try:
            plexserver = data['plexserverurl']
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
            embed = discord.Embed(title = "Plex Library not linked!", description=f"```❌ You don't have a Plex server linked to your Mazi account. Please add one as it is required to host sessions.```", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed, view=view)
            return
            # Check if the user has a Plex library linked
        try:
            plexlibrary = data['plexserverlibrary']
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
            libraryname = data["plexserverlibrary"]
            try:
                token, machineid, movie, key, plex = getHosting(data, moviechoice)
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
            try:
                # create room
                counts = countsdoc.get()
                previouscount = counts.to_dict()
                roomnames = ["Action", "Animation", "Horror", "Adventure", "Comedy", "Romance", "SciFi", "Fantasy", "Musical"]
                roomname = random.choice(roomnames)+"-"+str(previouscount["counts"])
                msg = await interaction.followup.send(f"```Please join this thread to join Watch Together session: {roomname}.```")
                thread = await interaction.channel.create_thread(name=f"Watch Together Session: {roomname}", message=msg, reason="Mazi created Watch Together room.", auto_archive_duration=60)
                await thread.send("```To join, please run '/join' in this thread.```")
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
                    u'Time Started': firestore.SERVER_TIMESTAMP,
                    u'Thread': channel,
                    u'MovieKey': key,
                    u'Server': plexserver,
                    u'MachineID': machineid,
                }, merge=True)
                #now add first user
                userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(discordid)
                userref.set({
                    u'id': userid,
                    u'thumb': thumb,
                    u'title': title,
                    u'email': email,
                    }, merge=True)
                #send message that the room is ready
                embed = discord.Embed(title = f"{roomname} is now open to join!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                embed.add_field(name = f'{data["plexserverlibrary"]}', value=f"We are watching {movie.title}!", inline = False)
                embed.add_field(name = 'Join Now', value="The room is now open to join! Run /join to join. Make sure you have linked your Plex and Discord accounts.", inline = False)
                if timetostart == 0:
                    embed.set_footer(text = "Room joining will not be disabled. Movie will start immediately. This means that nobody will be able to join.")
                else:
                    embed.set_footer(text = f"Room joining closes in {timetostart} minutes.")
                await thread.send(embed = embed)
            except Exception as e:
                print(e)
                print("error creating room")
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
                print('Adding count failed')
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
                        roomstart = requests.post(url, json = obj)
                    else:
                        db.collection(u'rooms').document(roomname).delete()
                        await thread.send(f"```Joining for {roomname} is closed. Open Plex on any device and accept the friend request if you are not already friends with the hoster. Then in 5 minutes, join the Watch Together session. {movie.title.capitalize()} will begin shortly.```")
                        await asyncio.sleep(timetostart*60)
                        roomstart = requests.post(url, json = obj)
                    await thread.send(f"```{roomname} has now started watching {movie.title}!```")
                except:
                    embed = discord.Embed(title = "Server not accessible!", description=f"```❌ Something went wrong and couldn't get a room set up. Please try again later or report this as an error using /project.```", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                    embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                    await interaction.followup.send(embed = embed, view=view)
                    return
            except: 
                embed = discord.Embed(title = "Server not accessible!", description=f"```❌ Something went wrong and couldn't get a room set up. Please try again later or report this as an error using /project.```", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
                embed.set_footer(text = f"{interaction.user.display_name}'s {libraryname}")
                await interaction.followup.send(embed = embed, view=view)
                return

def getHosting(data, moviechoice):
    try:
        encrypted = data["plexauth"]
        secret_key = config('AESKEY')
        encrypted = encrypted.split(':')
        nonce = b64decode(encrypted[0])
        encrypted = b64decode(encrypted[1])
        box = SecretBox(bytes(secret_key, encoding='utf8'))
        plexauth = box.decrypt(encrypted, nonce).decode('utf-8')
        plexurl = data["plexserverurl"]
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
        movie = plex.library.section(data["plexserverlibrary"]).get(moviechoice)
        key = movie.ratingKey
        return token, machineid, movie, key, plex
    except:
        return None

async def setup(client):
    await client.add_cog(Host(client))