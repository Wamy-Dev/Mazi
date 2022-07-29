#    ______               __  __            __                  
#   / ____/___ _____ _   / / / /_  ______  / /____  ___________ 
#  / __/ / __ `/ __ `/  / /_/ / / / / __ \/ __/ _ \/ ___/ ___(_)
# / /___/ /_/ / /_/ /  / __  / /_/ / / / / /_/  __/ /  (__  )   
#/_____/\__, /\__, /  /_/ /_/\__,_/_/ /_/\__/\___/_/  /____(_)  
#      /____//____/                                             
# 
import discord
from discord.ext import commands
from quart import Quart
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
#quart
app = Quart(__name__)
@app.route("/", methods = ["get"])
async def index():
    return '<h3><center>Mazi bot is up! ✔</center></h3>', 200
#firebase
cred = credentials.Certificate("./creds.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
#counts
doc = db.collection(u'counts').document(u'counts')
#discord
CLIENTTOKEN = config('CLIENTTOKENT')
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = '>', intents=intents)
client.remove_command('help')
@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}(ID: {client.user.id})')
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = ">help"))#sets status as "Watching:!help"
@client.command()
async def eggotyou(ctx):
    await ctx.send('Fine. You got me... screenshot this and send it to me on my discord to have your name put in the source code!', delete_after=5)
    await ctx.message.delete()
@client.command()
async def project(ctx):
    embed = discord.Embed(title = "Mazi Github", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://github.com/Wamy-Dev/Mazi', inline = False)
    embed.set_footer(text = "If you like this project please donate using >donate.")
    await ctx.send(embed = embed)
@client.command()
async def website(ctx):
    embed = discord.Embed(title = "Mazi Website", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://mazi.pw', inline = False)
    embed.set_footer(text = "If you like this project please donate using >donate.")
    await ctx.send(embed = embed)
@client.command()
async def donate(ctx):
    embed = discord.Embed(title = "Donate to the project", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://homeonacloud.com/donate', inline = False)
    embed.set_footer(text = "If you like this project please donate using >donate.")
    await ctx.send(embed = embed)
@client.command()
async def ping(ctx):
    txt = str(f"""```css\nIm not too slow right? {round(client.latency * 1000)}ms.```""")
    await ctx.send(txt)
@client.command()
async def counts(ctx):
    counts = doc.get()
    previouscount = counts.to_dict()
    txt = str(f"""```css\nThe bot has hosted movie night {str(previouscount["counts"])} times.```""")
    await ctx.send(txt)
@client.command(pass_context = True, aliases = ['Help'])
async def help(ctx):
    embed = discord.Embed(title = "Here is a command list:", colour= discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '>host', value='Start a movie session.', inline = False)
    embed.add_field(name = '>join', value='If there is an active session, join it.', inline = False)
    embed.add_field(name = '>link', value='Link your account to plex.', inline = False)
    embed.add_field(name = '>ping', value='Shows the ping between the bot and the user.', inline = False)
    embed.add_field(name = '>project', value='View the project Github.', inline = False)
    embed.add_field(name = '>website', value='View the Mazi website.', inline = False)
    embed.add_field(name = '>donate', value='Donate to the project.', inline = False)
    embed.add_field(name = '>counts', value='See how many times the bot has hosted a movie night globally.', inline = False)
    await ctx.send(embed = embed)
@client.command()
async def link(ctx):
    embed = discord.Embed(title = "Start linking accounts", colour = discord.Colour.from_rgb(229,160,13))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '🔗', value='https://mazi.pw/user', inline = False)
    embed.set_footer(text = "If you like this project please donate using >donate.")
    await ctx.send(embed = embed)
#big boy commands
@client.command()
async def movies(ctx):
    discordid = ctx.message.author.id
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
                if len(serverurl)>0:
                    serverurl = True
            except:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                embed.add_field(name = 'Link accounts', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await ctx.send(embed = embed)
                break
            if plexstatus & discordstatus & serverurl:
                try:
                    moviefields = []
                    for movie in getMovies(data):
                        moviefields.append(movie)
                    movies = ""
                    for items in moviefields:
                        movies += f"{items}\n"
                    #math
                    if len(moviefields) == 0:
                        await ctx.send("```❌No movies in Plex Movie library.```")
                    if len(moviefields) > 0:
                        embed = discord.Embed(title = "Available Plex Movies", description=movies, colour = discord.Colour.from_rgb(229,160,13))
                        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                        embed.set_footer(text = f"{ctx.message.author}'s movies")
                        await ctx.send(embed = embed)
                    if len(movies) > 4096:
                        await ctx.send("```❌ You have too many movies to display.```")
                except Exception as e:
                    print(e)
                    await ctx.send("```❌ Your Plex Server is not accessible!```")
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            embed.set_footer(text = "If you like this project please donate using >donate.")
            await ctx.send(embed = embed)
    except Exception as e:
        print(e) 
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        embed.set_footer(text = "If you like this project please donate using >donate.")
        await ctx.send(embed = embed)
def getMovies(data):
    #first login
    try:
        #convert from aes
        encrypted = data["plexauth"]
        secret_key = config('AESKEY')
        encrypted = encrypted.split(':')
        nonce = b64decode(encrypted[0])
        encrypted = b64decode(encrypted[1])
        box = SecretBox(bytes(secret_key, encoding='utf8'))
        plexauth = box.decrypt(encrypted, nonce).decode('utf-8')
        plex = PlexServer(data["plexserverurl"], plexauth)
        movies = plex.library.section('Movies')
    except Exception as e:
        print(e)
    list = []
    for video in movies.search():
        list.append(video.title)
        return(list)
@client.command()
async def host(ctx):
    discordid = ctx.message.author.id
    discordid = str(discordid)
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
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
                if len(serverurl)>0:
                    serverurl = True
            except:
                embed = discord.Embed(title = "You haven't provided all information!", colour = discord.Colour.from_rgb(229,160,13))
                embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                embed.add_field(name = 'Link accounts', value='https://mazi.pw/user', inline = False)
                embed.set_footer(text = "If you want to host you need all information.")
                await ctx.send(embed = embed)
                break
            if plexstatus & discordstatus & serverurl:
                #ask what movie to watch and get rating key from it.
                try:
                    embed = discord.Embed(title = "What movie would you like to host?", colour = discord.Colour.from_rgb(229,160,13))
                    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                    embed.set_footer(text = "Please send exact title.")
                    await ctx.send(embed = embed)
                    message = await client.wait_for('message', check=check, timeout=30)
                    moviechoice = message.content
                    try:
                        try:
                            encrypted = data["plexauth"]
                            secret_key = config('AESKEY')
                            encrypted = encrypted.split(':')
                            nonce = b64decode(encrypted[0])
                            encrypted = b64decode(encrypted[1])
                            box = SecretBox(bytes(secret_key, encoding='utf8'))
                            plexauth = box.decrypt(encrypted, nonce).decode('utf-8')
                            plex = PlexServer(data["plexserverurl"], plexauth)
                        except:
                            print("failture")
                        token = plex._token
                        machineid = plex.machineIdentifier
                        movie= plex.library.section('Movies').get(moviechoice)
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
                            channel = ctx.channel.id
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
                                    u'title': title
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
                                await ctx.send('```❌ Something went wrong and the movie couldnt get a room set up. Please try again, or report this using ">project"```')
                            embed = discord.Embed(title = f"{roomname} is now open to join!", colour = discord.Colour.from_rgb(229,160,13))
                            embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                            embed.add_field(name = 'Movie', value=f"We are watching {movie.title}!", inline = False)
                            embed.add_field(name = 'Join Now', value="The room is now open to join! Run >join to join. Make sure you have linked your Plex and Discord accounts.", inline = False)
                            embed.set_footer(text = "Room joining closes in 10 minutes.")
                            await ctx.send(embed = embed)
                            await asyncio.sleep(600)
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
                                        users.append(data)
                                url = f"https://together.plex.tv/rooms?X-Plex-Token={token}"
                                obj = {
                                        "sourceUri": f"server://{machineid}/com.plexapp.plugins.library/library/metadata/{moviekey}",
                                        "title": movie.title,
                                        "users": users
                                    }
                                try:
                                    db.collection(u'rooms').document(roomname).delete()
                                    roomstart = requests.post(url, json = obj)
                                    await ctx.send("```Joining for movie night is closed. The lights are off and the popcorn is out. Open Plex on any device and join the Watch Together Session! The movie will begin shortly.```")
                                except:
                                    await ctx.send('```❌ Something went wrong and the movie couldnt get a room set up. Please try again, or report this using ">project"```')
                            except: 
                                await ctx.send('```❌ Something went wrong and the movie couldnt get a room set up. Please try again, or report this using ">project"```')
                        except:
                            await ctx.send('```❌ Something went wrong and the movie couldnt get a room set up. Please try again, or report this using ">project"```')
                    except:
                        await ctx.send('```❌ Movie not found in your library. Please check spelling or run ">movies" to view all of your movies.```')
                except asyncio.TimeoutError:
                    await ctx.send('```❌ Timed out.```')
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            embed.set_footer(text = "If you like this project please donate using >donate.")
            await ctx.send(embed = embed)
    except Exception as e:
        print(e) 
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        embed.set_footer(text = "If you like this project please donate using >donate.")
        await ctx.send(embed = embed)
@client.command()
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
                    #add to roomname
                    try:
                        userref = db.collection(u'rooms').document(roomname).collection(u'Users').document(discordid)
                        userref.set({
                            u'plexuserid': userid,
                            u'plexthumb': thumb,
                            u'plextitle': title,
                            u'discordid': discordid
                            }, merge=True)
                        await ctx.send(f"```You have joined {roomname}!```")
                    except:
                        await ctx.send("```❌ There was an error joining the room.```")
                if empty:
                    await ctx.send("peepee")
        if empty:
            embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
            embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
            embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
            embed.set_footer(text = "If you like this project please donate using >donate.")
            await ctx.send(embed = embed)
    except Exception as e:
        embed = discord.Embed(title = "No account found!", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.add_field(name = 'Create an account', value='https://mazi.pw/user', inline = False)
        embed.set_footer(text = "If you like this project please donate using >donate.")
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
#discord_thread = async_discord_thread()
#app.run(host="0.0.0.0", port="5001")
client.run(CLIENTTOKEN)