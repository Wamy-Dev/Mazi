from plexapi.myplex import MyPlexAccount
import discord
from discord.ext import commands
from plexapi.server import PlexServer
from decouple import config
import asyncio
from argon2 import PasswordHasher
import sqlite3

CLIENTTOKEN = config('CLIENTTOKEN')
client = commands.Bot(command_prefix = '>')
ph = PasswordHasher()


try: 
    connection = sqlite3.connect("creds.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE creds (discordid TEXT, plexuser TEXT, plexpass TEXT, plexserver TEXT)")
except:
    print("Table already present.")
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
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
    embed.add_field(name = '>ping', value='Shows the ping between the bot and the user.', inline = False)
    embed.add_field(name = '>project', value='View the project github.', inline = False)
    embed.add_field(name = '>donate', value='Donate to the project.', inline = False)
    embed.add_field(name = '>counts', value='See how much media has been shared using this bot.', inline = False)
    embed.add_field(name = '>link', value='Link your Plex and Discord accounts to share with your friends. Not required unless you host the session.', inline = False)
    embed.add_field(name = '>watch', value='Start a Plex Watch Togther session.', inline = False)
    await ctx.send(embed = embed)
@client.command(pass_context = True)
async def link(ctx):
    #gets user info
    discordid = ctx.message.author.id
    query = cursor.execute(f"SELECT * FROM creds WHERE discordid = {discordid}")
    if len(cursor.fetchall()) > 0:
        await ctx.send("```✔ Your account is already linked.```")
    else: 
        messageembed = discord.Embed(title = "Link your plex and your discord", color= discord.Color.from_rgb(160,131,196), description="🔗 Please check your pm's to link your accounts.")
        messageembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
        messageembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        dmembed = discord.Embed(title = "🤝 Please enter your Plex username.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).")
        dmembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
        dmembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        dmpassembed = discord.Embed(title = "🤝 Please enter your Plex password.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).")
        dmpassembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
        dmpassembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        dmserverembed = discord.Embed(title = "🤝 Please enter your Plex servername.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).")
        dmserverembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
        dmserverembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        await ctx.send(embed = messageembed)#tells user to link
        member = ctx.message.author
        discordid = ctx.message.author.id
        await ctx.message.author.send(embed = dmembed)
        try:
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
                account = MyPlexAccount(username, password)
                plex = account.resource(servername).connect()
            except:
                await ctx.message.author.send('```❌ Your credentials are incorrect. Please try again.```')
            try:
                passwordhash = ph.hash(password)#uses argon2id. Thanks to Capitaine J. Sparrow#0096 for the advice.
                print(passwordhash)
                if ph.verify(passwordhash, password):
                    cursor.execute(f'INSERT INTO creds VALUES ("{discordid}", "{username}", "{passwordhash}", "{servername}")')
                    connection.commit()
                    password = "null"#wipes previous password from mem
                else:
                    print("Failed to hash")
                await ctx.message.author.send('```✔ Encrypted and saved your credentials. You are now able to host watch together sessions.```')
            except Exception as e:
                await ctx.message.author.send('```❌ Something went wrong, please try again.```')
                print(e)
        except asyncio.TimeoutError:
            await ctx.message.author.send('```❌ Timed out, please run >link again in the server.```')
client.run(CLIENTTOKEN)