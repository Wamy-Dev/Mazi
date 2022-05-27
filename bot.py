import discord
from discord.ext import commands
from decouple import config
import sqlite3
from flask import Flask, request, redirect, render_template
import requests
from waitress import serve
import threading
import asyncio
from plexapi.myplex import MyPlexAccount
import functools
import typing
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import base64
import time
import aiosqlite
#import logging
#logging.basicConfig(level=logging.DEBUG)
CLIENT_ID = '978163786886311977'
CLIENT_SECRET = config('CLIENT_SECRET')
REDIRECT_URI = "http://127.0.0.1:5000/success"
SCOPE = "identify%20email"
DISCORD_LOGIN = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}&prompt=consent"
DISCORD_TOKEN = "https://discord.com/api/oauth2/token"
DISCORD_API = "https://discord.com/api"
KEYSALT = config('KEYSALT')
KEYPEPPER = config('KEYPEPPER')
SALT = config('SALT')
SALT = SALT.encode()
#init bot
CLIENTTOKEN = config('CLIENTTOKEN')
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or('>'), intents=intents)
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
client = Bot()
#all flask
app = Flask(__name__)
@app.route("/", methods = ["get"])
def index():
    return render_template('index.html')
@app.route("/login", methods = ["get"])
def login():
    return redirect(DISCORD_LOGIN)
@app.route("/success", methods = ["get"])
def success():
    code = request.args.get("code")
    useraccesstoken = getaccesstoken(code)
    userdata = getuserdata(useraccesstoken)
    useremail = userdata.get("email")
    userid = userdata.get("id")
    userid = str(userid)
    useravatar = userdata.get("avatar")
    useravatar = (f"https://cdn.discordapp.com/avatars/{userid}/"+useravatar+".png")
    connection = sqlite3.connect("creds.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO creds(discordid, discordemail) VALUES(?, ?)", (userid, useremail,))
    connection.commit()
    return render_template('success.html', useravatar = useravatar)
def getaccesstoken(code):
    payload = {
       "client_id": CLIENT_ID,
       "client_secret": CLIENT_SECRET,
       "grant_type": "authorization_code",
       "code": code,
       "redirect_uri": REDIRECT_URI,
       "scope": SCOPE
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    accesstoken = requests.post(url = DISCORD_TOKEN, data = payload, headers = headers)
    json = accesstoken.json()
    return json.get("access_token")
def getuserdata(useraccesstoken):
    url = DISCORD_API+"/users/@me"
    headers = {
        "Authorization": f"Bearer {useraccesstoken}"
    }
    userdata = requests.get(url = url, headers = headers)
    userjson = userdata.json()
    return userjson
def web():
    serve(app, host="127.0.0.1", port=5000)
#makes db if it does not exist
try: 
    connection = sqlite3.connect("creds.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE creds (discordid TEXT, discordemail TEXT, plexuser TEXT, plexpass TEXT, plexserver TEXT)")
    print("Created new table.")
except:
    print("Table already present.")
#basic commands
client.remove_command('help')
@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}(ID: {client.user.id}) ')
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = ">help"))
@client.command()
async def eggotyou(ctx):
    await ctx.send('Fine. You got me... screenshot this and send it to me on my discord to have your name put in the source code!', delete_after=5)
    await ctx.message.delete()
@client.command()
async def project(ctx):
    await ctx.send('```https://github.com/Wamy-Dev/Mazi```')
@client.command()
async def donate(ctx):
    await ctx.send('```https://homeonacloud.com/pages/donate```')
@client.command()
async def ping(ctx):
    await ctx.send(f'```I`m not too slow... right? {round(client.latency * 1000)}ms```')
@client.command(pass_context = True, aliases = ['Help', "h"])
async def help(ctx):
    embed = discord.Embed(title = "Here is a command list:", color= discord.Color.from_rgb(160,131,196))
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '>ping', value='Shows the ping between the bot and the user.', inline = False)
    embed.add_field(name = '>project', value='View the project github.', inline = False)
    embed.add_field(name = '>donate', value='Donate to the project.', inline = False)
    embed.add_field(name = '>counts', value='See how much media has been shared using this bot.', inline = False)
    embed.add_field(name = '>link', value='Link your Plex and Discord accounts to share with your friends. Not required unless you host the session.', inline = False)
    embed.add_field(name = '>unlink', value='Unlink your Plex and Discord accounts.', inline = False)
    embed.add_field(name = '>watch', value='Start a Plex Watch Togther session.', inline = False)
    await ctx.send(embed = embed)
@client.command(pass_context = True)
#unlink
async def unlink(ctx):
    discordid = ctx.message.author.id
    query = cursor.execute(f"SELECT * FROM creds WHERE discordid = ?", (discordid,))
    if len(cursor.fetchall()) > 0:
        class Confirm(discord.ui.View):
            def __init__(self, ctx):
                super().__init__(timeout=30)
                self.value = None
                self.ctx = ctx
            @discord.ui.button(label='Confirm', style=discord.ButtonStyle.red)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                cursor.execute(f"DELETE FROM creds WHERE discordid = ?", (discordid,))
                connection.commit()
                await interaction.response.send_message("```🖐 Unlinked account. If you would like to relink in the future, run >link again.```", ephemeral=False)
                self.value = True
                self.stop()
            @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message("```❌ Aborted by user. Did not delete link.```", ephemeral=False)
                self.value = False
                self.stop()
            async def on_timeout(self):
                await self.ctx.send("```❌ Timed out, did not delete link. If you meant to delete link, please run >unlink again and click confirm.```")
        embed = discord.Embed(title = "Click confirm to delete link", color= discord.Color.from_rgb(160,131,196), description="⚠ Are you sure you want to unlink your account? If not, please click the cancel button.")
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.set_footer(text=f'If you want to relink in the future, run >link again.')
        view = Confirm(ctx)
        await ctx.send(embed=embed, view=view)
        await view.wait()
    else:
        await ctx.send("```❌ You don't have an account linked to unlink...```")
#link
def blocking_func(username, password, servername):
    """A very blocking function"""
    account = MyPlexAccount(username, password)
    plex = account.resource(servername).connect()
async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await client.loop.run_in_executor(None, func)
def hash(password, discordemail):#thanks Capitaine J. Sparrow#0096 for the base code for this system
    kdf = Scrypt(
        salt=SALT,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    DERIVATED_SALT = kdf.derive(str.encode(discordemail))
    encryption_suite = AES.new(DERIVATED_SALT, AES.MODE_CBC, SALT)
    encrypted_pwd = encryption_suite.encrypt(password.encode() * 16)
    encrypted_pwd = base64.b64encode(encrypted_pwd)
    encrypted_pwd = encrypted_pwd.decode()
    return encrypted_pwd#returns base64string
def login(discordemail, encrypted_pwd):#thanks Capitaine J. Sparrow#0096 for the base code for this system
    kdf = Scrypt(
        salt=SALT,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    DERIVATED_SALT = kdf.derive(str.encode(discordemail))
    decryption_suite = AES.new(DERIVATED_SALT, AES.MODE_CBC, SALT)
    plain_text = decryption_suite.decrypt(encrypted_pwd)
    plain_text = base64.b64decode("utf_8")
    unhashedpassword=(plain_text[0: len(plain_text)//16]).decode("utf_8")
    print(unhashedpassword)
    return unhashedpassword
@client.command()
async def link(ctx):
    #checks if user is linked first
    discordid = ctx.message.author.id
    discordid = str(discordid)
    connection = sqlite3.connect("creds.db")
    cursor = connection.cursor()
    query = cursor.execute(f"SELECT * FROM creds WHERE discordid = ?", (discordid,))
    if len(cursor.fetchall()) > 0:
        query = cursor.execute(f"SELECT plexpass FROM creds WHERE discordid = ?", (discordid,)).fetchall()
        if len(query) > 0:
            await ctx.send("```✔ Your account is already linked.```")
        else: 
            await ctx.send("```❌ You did not finish linking your account. Please run >unlink and then >link again to restart the process.```")
    else:#FUTURE FEATURE: MAKE A TIMEOUT FOR IF USER DID NOT CLICK LINK, IVE TRIED SO HARD ON THIS AND HAVE FOUND NO SOLUTION
        #make user click oauth2 link to recieve email
        firstmessageembed = discord.Embed(title = "Authorize your account", color= discord.Color.from_rgb(160,131,196), description="🔗 Please click [HERE](http://127.0.0.1:5000/login) to get started.")
        firstmessageembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        firstmessageembed.set_footer(text=f'You have 60 seconds to authorize.')
        await ctx.send(embed = firstmessageembed)
        #wait until email is available
        db = await aiosqlite.connect("creds.db")
        cursor = await db.execute(f"SELECT discordemail FROM creds WHERE discordid = ?", (discordid,))
        data = await cursor.fetchall()
        try:
            while len(data) == 0:
                db = await aiosqlite.connect("creds.db")
                cursor = await db.execute(f"SELECT discordemail FROM creds WHERE discordid = ?", (discordid,))
                data = await cursor.fetchall()
            else:
                #got email
                messageembed = discord.Embed(title = "Link your Plex and your Discord", color= discord.Color.from_rgb(160,131,196), description="🔗 Thank you for authorizing. Please check your pm's to link your accounts.")
                messageembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                messageembed.set_footer(text=f'This method is temporary and will be fixed in the future. Only send sensitive data to Mazi#2364. ♥')
                await ctx.send(embed = messageembed)
                userdmembed = discord.Embed(title = "🤝 Please enter your Plex username", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [128bit AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
                userdmembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                userdmembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
                await ctx.message.author.send(embed = userdmembed)
                try:#in try because we want a timeout
                    dmpassembed = discord.Embed(title = "🤝 Please enter your Plex password.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [128bit AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
                    dmpassembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                    dmpassembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
                    dmserverembed = discord.Embed(title = "🤝 Please enter your Plex servername", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [128bit AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
                    dmserverembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                    dmserverembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
                    member = ctx.message.author
                    username = await client.wait_for('message', check = lambda x: x.channel == member.dm_channel and x.author == member, timeout=30)
                    username = username.content
                    await ctx.message.author.send(embed = dmpassembed)
                    password = await client.wait_for('message', check = lambda x: x.channel == member.dm_channel and x.author == member, timeout=30)
                    password = password.content
                    await ctx.message.author.send(embed = dmserverembed) 
                    servername = await client.wait_for('message', check = lambda x: x.channel == member.dm_channel and x.author == member, timeout=30)
                    servername = servername.content
                    await ctx.message.author.send('```⏰ Please be patient while I check your credentials. This might take a couple moments.```')
                    try:
                        r = await run_blocking(blocking_func, username, password, servername,)
                        #now to encrypt passwords
                        cursor = await db.execute(f"SELECT discordemail FROM creds WHERE discordid = ?", (discordid,))
                        discordemail = await cursor.fetchall()
                        discordemail = discordemail[0][0]
                        encryptedpwd = hash(password, discordemail)
                        password = "NULL"#wiping from mem
                        discordemail = "NULL"#wiping from mem
                        try:
                            delete = await db.execute("UPDATE creds SET discordemail=NULL WHERE discordid = ?", (discordid,))
                            commit = await db.commit()
                            insert = await db.execute("UPDATE creds SET plexuser=?, plexpass=?, plexserver=? WHERE discordid = ?", (username, encryptedpwd, servername,discordid,))
                            commit = await db.commit()
                        except Exception as e: print(e)
                        await ctx.message.author.send('```✔ Encrypted and saved your credentials. You are now able to host watch together sessions.```')
                    except:
                        await ctx.message.author.send('```❌ Your credentials are incorrect. Please try again.```')
                except asyncio.TimeoutError:
                    await ctx.message.author.send('```❌ Timed out, please run >link again in the server.```')
        except asyncio.TimeoutError: 
            await ctx.send('```❌ Timed out, please run >link again.```')

        
            



        

threading.Thread(target=web, daemon=True).start()#starts web app
client.run(CLIENTTOKEN)
