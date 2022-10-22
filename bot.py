#    ______               __  __            __                  
#   / ____/___ _____ _   / / / /_  ______  / /____  ___________ 
#  / __/ / __ `/ __ `/  / /_/ / / / / __ \/ __/ _ \/ ___/ ___(_)
# / /___/ /_/ / /_/ /  / __  / /_/ / / / / /_/  __/ /  (__  )   
#/_____/\__, /\__, /  /_/ /_/\__,_/_/ /_/\__/\___/_/  /____(_)  
#      /____//____/                                             
# directlycrazy.1812
# Mato.5201
import requests 
import urllib3
import logging
session = requests.Session()
session.verify = False
urllib3.disable_warnings()
import discord
from discord import app_commands
from discord.ext import commands
from quart import Quart, render_template
from decouple import config
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import asyncio
from threading import Thread
from plexapi.server import PlexServer
from base64 import b64decode
from nacl.secret import SecretBox
import random
import requests
from datetime import datetime
from humanfriendly import format_timespan
#quart
app = Quart(__name__)
logging.getLogger('quart.serving').setLevel(logging.ERROR)
ready = False
inittime = datetime.now()
@app.route("/", methods = ["get"])
async def index():
    while ready:
        latencies = []
        for i in client.latencies:
            data = {}
            shard = i[0]
            latency = round(i[1] * 1000)#in ms
            data["shard"] = shard
            data["latency"] = latency
            uptime = datetime.now() - inittime
            secuptime = uptime.total_seconds()
            totaluptime = format_timespan(secuptime)
            data["uptime"] = totaluptime
            latencies.append(data)
        members = 0
        servers = client.guilds
        servercount = {}
        for guild in servers:
            id = guild.shard_id
            try:
                count = servercount[id]
            except:
                count = 0
            count += 1
            servercount[id] = count
            members += guild.member_count
        timeutc = str(datetime.utcnow())
        timenow = timeutc[:-7]
        #get full number of servers
        serverstotal = len(servers)
        servers = serverstotal
        shardcount = client.shard_count
        return await render_template("statuspage.html", latencies=latencies, members=members, servercount=servercount, timenow=timenow, serverstotal=serverstotal, shardcount=shardcount)
    else:
        return await render_template("failpage.html")
#firebase
cred = credentials.Certificate("./creds.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
#counts
doc = db.collection(u'counts').document(u'counts')
#discord
CLIENTTOKEN = config('CLIENTTOKEN')
intents = discord.Intents.default()
client = commands.AutoShardedBot(command_prefix = '>', intents=intents)
client.remove_command('help')
@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}(ID: {client.user.id})')
    print(f'Shards: {client.shard_count}')
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "/help"))
    global ready
    ready = True
    await asyncio.sleep(5)
    await client.tree.sync()
    print("Tree synced")
@client.hybrid_command(name = "eggotyou", description = "?")
async def eggotyou(ctx):
    await ctx.send('Fine. You got me... screenshot this and send it to me on my Discord server to have your name put in the source code!', delete_after=5)
@client.hybrid_command(name = "project", description = "View the Mazi Github project page.")
async def project(ctx):
    embed = discord.Embed(title = "Mazi Github", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://github.com/Wamy-Dev/Mazi', inline = False)
    await ctx.send(embed = embed)
@client.hybrid_command(name = "faq", description = "Read the Mazi F.A.Q.")
async def project(ctx):
    embed = discord.Embed(title = "Mazi F.A.Q.", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://github.com/Wamy-Dev/Mazi/wiki/FAQ', inline = False)
    await ctx.send(embed = embed)
@client.hybrid_command(name = "website", description = "View the Mazi website.")
async def website(ctx):
    embed = discord.Embed(title = "Mazi Website", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://mazi.pw', inline = False)
    await ctx.send(embed = embed)
@client.hybrid_command(name = "donate", description = "Doante to the Mazi project.")
async def donate(ctx):
    embed = discord.Embed(title = "Donate to the project", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://homeonacloud.com/donate', inline = False)
    await ctx.send(embed = embed)
@client.hybrid_command(name = "ping", description = "View the ping between Discord and Mazi.")
async def ping(ctx):
    txt = str(f"""```css\nIm not too slow right? {round(client.latency * 1000)}ms.```""")
    await ctx.send(txt)
@client.hybrid_command(name = "counts", description = "View how many movie nights have been hosted globally.")
async def counts(ctx):
    counts = doc.get()
    previouscount = counts.to_dict()
    txt = str(f"""```css\nThe bot has hosted movie night {str(previouscount["counts"] - 1)} times.```""")
    await ctx.send(txt)
@client.hybrid_command(name = "help", description = "Shows the help dialogue.", pass_context = True, aliases = ['Help'])
async def help(ctx):
    list = ["Now with 100% more help!", "Now with slash commands!", "Cool cats watch movies.", "Runs on Plex and a little love.", "Help support Mazi by running /donate!", "Now showing, your movies!"]
    embed = discord.Embed(title = "Here is a command list:", colour= discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '/host', value='Start a movie session.', inline = False)
    embed.add_field(name = '/join', value='If there is an active session, join it.', inline = False)
    embed.add_field(name = '/movies', value='Get all movies that are available to watch.', inline = False)
    embed.add_field(name = '/link', value='Link your Discord and Plex accounts.', inline = False)
    embed.add_field(name = '/ping', value='Shows the ping between the bot and the user.', inline = False)
    embed.add_field(name = '/project', value='View the project Github.', inline = False)
    embed.add_field(name = '/website', value='View the Mazi website.', inline = False)
    embed.add_field(name = '/donate', value='Donate to the project.', inline = False)
    embed.add_field(name = '/counts', value='See how many times the bot has hosted a movie night globally.', inline = False)
    embed.add_field(name = '/faq', value='Read the Mazi F.A.Q.', inline = False)
    embed.set_footer(text = random.choice(list))
    await ctx.send(embed = embed)
@client.hybrid_command(name = "link", description = "Link your Plex and Discord accounts.")
async def link(ctx):
    embed = discord.Embed(title = "Start linking accounts", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://mazi.pw/user', inline = False)
    await ctx.send(embed = embed)
#big boy commands
@client.tree.command(name = "movies", description = "View the all the movies available to watch on your linked Plex account.")
async def movies(interaction: discord.Interaction):
    await interaction.response.defer()
    discordid = interaction.user.id
    discordid = str(discordid)
    #get data
    try:
        docs = db.collection(u'users').where(u'discordid', u'==', discordid).stream()
        empty = True
        for doc in docs:
            empty = False
            data = doc.to_dict()
            try:
                discordstatus = data["discord"]
                plexstatus = data["plex"]
                serverurl = data["plexserverurl"]
                serverlibrary = data["plexserverlibrary"]
                libraryname = data["plexserverlibrary"]
                if len(serverurl)>0 and len(serverlibrary)>0:
                    serverurl = True
                    serverlibrary = True
                else:
                    embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                    embed.description("You may be missing either your serverURL or your serverLibrary. Please add them using the link.")
                    embed.add_field(name = 'Add information', value='https://mazi.pw/user', inline = False)
                    embed.set_footer(text = "If you want to host you need all information.")
                    await interaction.followup.send(embed = embed)
                    break
            except:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                embed.description("You may be missing either your serverURL or your serverLibrary. Please add them using the link.")
                embed.add_field(name = 'Add information', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await interaction.followup.send(embed = embed)
                break
            if plexstatus & discordstatus & serverurl & serverlibrary:
                try:
                    moviefields = []
                    for movie in getMovies(data):
                        moviefields.append(movie)
                    movieslist = ""
                    for items in moviefields:
                        movieslist += f'{items}\n'
                    if len(movieslist) == 0:
                        await interaction.followup.send("```❌ No movies in Plex Movie library.```")
                    if len(movieslist) > 4096:
                        await interaction.followup.send("```❌ You have too many movies to display.```")
                    if len(movieslist) < 4096:
                        embed = discord.Embed(title = f"Available items in {libraryname}", description=movieslist, colour = discord.Colour.from_rgb(229,160,13))
                        embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                        embed.set_footer(text = f"{interaction.user}'s {libraryname}")
                        await interaction.followup.send(embed = embed)
                except Exception as e:
                    print(e)
                    embed = discord.Embed(title = "Your Plex Server is not accessible!", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                    embed.add_field(name = 'Edit server info', value='https://mazi.pw/user', inline = False)
                    embed.add_field(name = 'Why?', value='[Read the FAQ](https://github.com/Wamy-Dev/Mazi/wiki/FAQ#the-bot-says-you-server-is-inaccessible-but-i-can-access-it-just-fine-why)', inline = False)
                    await interaction.followup.send(embed = embed)
            else:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                embed.description("You may be missing either your serverURL or your serverLibrary. Please add them using the link.")
                embed.add_field(name = 'Add information', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await interaction.followup.send(embed = embed)
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            await interaction.followup.send(embed = embed)
    except Exception as e:
        print(e) 
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        await interaction.followup.send(embed = embed)
def getMovies(data):
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
        movies = plex.library.section(data["plexserverlibrary"])
    except Exception as e:
        print(e)
        return None
    list = []
    for video in movies.all():
        list.append(video.title)
    return(list)
@client.tree.command(name = "host", description = "Host a Plex movie watch together with your friends.")
@app_commands.describe(moviechoice = "The exact title of the movie you want to watch.")
async def host(interaction: discord.Interaction, moviechoice: str):
    await interaction.response.defer()
    discordid = interaction.user.id
    discordid = str(discordid)
    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel
    #get data
    try:
        docs = db.collection(u'users').where(u'discordid', u'==', discordid).stream()
        empty = True
        for doc in docs:
            empty = False
            data = doc.to_dict()
            try:
                discordstatus = data["discord"]
                plexstatus = data["plex"]
                serverurl = data["plexserverurl"]
                serverlibrary = data["plexserverlibrary"]
                if len(serverurl)>0 and len(serverlibrary)>0:
                    serverurl = True
                    serverlibrary = True
                else:
                    embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                    embed.add_field(name = 'Add information', value='https://mazi.pw/user', inline = False)
                    embed.set_footer(text = "If you want to host you need all information.")
                    await interaction.followup.send(embed = embed)
                    break
            except:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                embed.add_field(name = 'Add information', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await interaction.followup.send(embed = embed)
                break
            if plexstatus & discordstatus & serverurl & serverlibrary:
                #ask what movie to watch and get rating key from it.
                    try:
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
                        except Exception as e:
                            print(e)
                            embed = discord.Embed(title = "Your Plex Server is not accessible!", colour = discord.Colour.from_rgb(229,160,13))
                            embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                            embed.add_field(name = 'Edit server info', value='https://mazi.pw/user', inline = False)
                            embed.add_field(name = 'Why?', value='[Read the FAQ](https://github.com/Wamy-Dev/Mazi/wiki/FAQ#the-bot-says-you-server-is-inaccessible-but-i-can-access-it-just-fine-why)', inline = False)
                            await interaction.followup.send(embed = embed)
                            break
                        token = plex._token
                        machineid = plex.machineIdentifier
                        movie= plex.library.section(data["plexserverlibrary"]).get(moviechoice)
                        key = movie.ratingKey
                        try:
                            #making room name
                            doc = db.collection(u'counts').document(u'counts')
                            counts = doc.get()
                            previouscount = counts.to_dict()
                            roomnames = ["Action", "Animation", "Horror", "Adventure", "Comedy", "Romance", "SciFi", "Fantasy", "Musical"]
                            roomname = random.choice(roomnames)+"-"+str(previouscount["counts"])
                            userid = data["plexid"]
                            thumb = data["plexthumb"]
                            title = data["plextitle"]
                            email = data["plexemail"]
                            channel = interaction.channel.id
                            discordid = discordid
                            #add to firebase to allow joining
                            try:
                                ref = db.collection(u'rooms').document(roomname)
                                ref.set({
                                    u'Time Started': firestore.SERVER_TIMESTAMP,
                                    u'Channel': channel,
                                    u'MovieKey': key,
                                    u'Server': serverurl,
                                    u'MachineID': machineid,
                                }, merge=True)
                                #now add users to that document
                                userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(discordid)
                                userref.set({
                                    u'id': userid,
                                    u'thumb': thumb,
                                    u'title': title,
                                    u'email': email,
                                    }, merge=True)
                                try:
                                    doc = db.collection(u'counts').document(u'counts')
                                    counts = doc.get()
                                    previouscount = counts.to_dict()
                                    newcount = int(previouscount['counts']) + 1
                                    doc.update({u'counts': newcount})
                                except Exception as e: 
                                    print(e)
                                    print('Adding count failed')
                            except Exception as e:
                                print(e)
                                await interaction.followup.send('```❌ Something went wrong and the movie couldnt get a room set up. Error 280. Please try again, or report this using "/project"```')
                            embed = discord.Embed(title = f"{roomname} is now open to join!", colour = discord.Colour.from_rgb(229,160,13))
                            embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
                            embed.add_field(name = f'{data["plexserverlibrary"]}', value=f"We are watching {movie.title}!", inline = False)
                            embed.add_field(name = 'Join Now', value="The room is now open to join! Run /join to join. Make sure you have linked your Plex and Discord accounts.", inline = False)
                            embed.set_footer(text = "Room joining closes in 5 minutes.")
                            await interaction.followup.send(embed = embed)
                            await asyncio.sleep(300)
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
                                    db.collection(u'rooms').document(roomname).delete()
                                    await interaction.followup.send(f"```Joining for {roomname} is closed. Open Plex on any device and accept the friend request if you are not already friends with the hoster. Then in 5 minutes, join the Watch Together session. {movie.title.capitalize()} will begin shortly.```")
                                    await asyncio.sleep(300)
                                    roomstart = requests.post(url, json = obj)
                                    await interaction.followup.send(f"```{roomname} has now started watching {movie.title}!```")
                                except:
                                    await interaction.followup.send('```❌ Something went wrong and the movie couldnt get a room set up. Error 316. Please try again, or report this using "/project"```')
                            except: 
                                await interaction.followup.send('```❌ Something went wrong and the movie couldnt get a room set up. Error 289. Please try again, or report this using "/project"```')
                        except:
                            await interaction.followup.send('```❌ Something went wrong and the movie couldnt get a room set up. Error 238. Please try again, or report this using "/project"```')
                    except:
                        await interaction.followup.send('```❌ Movie not found in your library. Please check spelling or run "/movies" to view all of your movies.```')
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            await interaction.followup.send(embed = embed)
    except Exception as e:
        print(e) 
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user, icon_url = interaction.user.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        await interaction.followup.send(embed = embed)
@client.hybrid_command(name = "join", description = "Join an active Plex watch together session room.")
async def join(ctx):
    discordid = ctx.message.author.id
    discordid = str(discordid)
    channel = ctx.channel.id
    #get data
    try:
        docs = db.collection(u'users').where(u'discordid', u'==', discordid).stream()
        empty = True
        for doc in docs:
            empty = False
            data = doc.to_dict()
            try:
                discordstatus = data["discord"]
                plexstatus = data["plex"]
            except:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                embed.add_field(name = 'Link accounts', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await ctx.send(embed = embed)
                break
            if plexstatus & discordstatus:
                #get all showings in channel
                try:
                    docs = db.collection(u'rooms').where(u'Channel', u'==', channel).stream()
                    norooms = True
                    for rooms in docs:
                        norooms = False
                        roomname = rooms.id
                    if norooms:
                        await ctx.send("```❌ There are no open rooms to join!```")
                        break
                except:
                    await ctx.send("```❌ There are no open rooms to join!```")
                    break
                #get user information
                document = db.collection(u'users').where(u'discordid', u'==', discordid).stream()
                empty = True
                for doc in document:
                    empty = False
                    data = doc.to_dict()
                    userid = data["plexid"]
                    thumb = data["plexthumb"]
                    title = data["plextitle"]
                    email = data["plexemail"]
                    #add to roomname
                    try:
                        userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(discordid)
                        userref.set({
                            u'id': userid,
                            u'thumb': thumb,
                            u'title': title,
                            u'email': email
                            }, merge=True)
                        await ctx.send(f"```You have joined {roomname}!```")
                    except:
                        await ctx.send("```❌ There was an error joining the room.```")
                if empty:
                    await ctx.send("```❌ There was an error joining the room.```")
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            await ctx.send(embed = embed)
    except Exception as e:
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        await ctx.send(embed = embed)
class async_discord_thread(Thread):
    #thanks @FrankWhoee for this code snippet
    def __init__(self):
        Thread.__init__(self)
        self.loop = asyncio.get_event_loop()
        self.start()
    async def starter(self):
        await client.start(CLIENTTOKEN)
    def run(self):
        self.name = 'Discord.py'
        self.loop.create_task(self.starter())
        self.loop.run_forever()
discord_thread = async_discord_thread()
app.run(host="0.0.0.0", port="5001")