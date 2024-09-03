#    ______               __  __            __                  
#   / ____/___ _____ _   / / / /_  ______  / /____  ___________ 
#  / __/ / __ `/ __ `/  / /_/ / / / / __ \/ __/ _ \/ ___/ ___(_)
# / /___/ /_/ / /_/ /  / __  / /_/ / / / / /_/  __/ /  (__  )   
#/_____/\__, /\__, /  /_/ /_/\__,_/_/ /_/\__/\___/_/  /____(_)  
#      /____//____/                                             
# directlycrazy.1812
# Mato.5201
# Andr01dx86.1886
# DARTUBE.6145
# Cholo Lord.6202
# cocolaninano#7812
# piny.
# kayliatalon
# yiga_
# cekirge1972
# Matthew Ariel
import requests 
import os
import urllib3
import logging
from logging import getLogger
from quart.logging import default_handler
getLogger('quart.serving').removeHandler(default_handler)
getLogger('quart.serving').setLevel(logging.ERROR)
session = requests.Session()
session.verify = False
urllib3.disable_warnings()
import discord
from discord.ext import commands
from quart import Quart, render_template
from decouple import config
import firebase_admin
from firebase_admin import credentials
import asyncio
from threading import Thread
import requests
from datetime import datetime
from humanfriendly import format_timespan
#quart
app = Quart(__name__)
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
cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(cred)
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

# @client.tree.command(name="reload", description="Reloads a cog.")
# async def reload(interaction: discord.Interaction, cog: str = None):
#     try:
#         await client.reload_extension(f"cogs.{cog}")
#         await interaction.response.send_message(f"Reloaded {cog}")
#         await client.tree.sync()
#     except Exception as e:
#         await interaction.response.send_message(f"{e}")

class async_discord_thread(Thread):
    #thanks @FrankWhoee for this code snippet
    def __init__(self):
        Thread.__init__(self)
        self.loop = asyncio.get_event_loop()
        self.start()
    async def starter(self):
        async def load_extensions():
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    await client.load_extension(f"cogs.{filename[:-3]}")
        await load_extensions()
        await client.start(CLIENTTOKEN)
    def run(self):
        self.name = 'Discord.py'
        self.loop.create_task(self.starter())
        self.loop.run_forever()
discord_thread = async_discord_thread()
app.run(host="0.0.0.0", port="5001")
# async def load_extensions():
#     for filename in os.listdir("./cogs"):
#         if filename.endswith(".py"):
#             await client.load_extension(f"cogs.{filename[:-3]}")
# async def start():
#     await load_extensions()
#     await client.start(CLIENTTOKEN)
# asyncio.run(start())
