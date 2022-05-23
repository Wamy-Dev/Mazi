from plexapi.myplex import MyPlexAccount
import discord
from discord.ext import commands
from plexapi.server import PlexServer
from decouple import config
import asyncio

CLIENTTOKEN = config('CLIENTTOKEN')
client = commands.Bot(command_prefix = '>')
client.remove_command('help')
@client.event
async def on_ready():
    print(f'Bot is ready. Logged in as {client.user}(ID: {client.user.id}) ')
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = ">help"))
@client.command()
async def eggotyou(ctx):
    await ctx.send('Fine. You got me... screenshot this and send it to me on my discord to have your name put in the source code!', delete_after=5)
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
    messageembed = discord.Embed(title = "Link your plex and your discord", color= discord.Color.from_rgb(160,131,196))
    messageembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
    messageembed.add_field(name = '🔗', value='Please check your pms to link your accounts', inline = True)
    messageembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
    dmembed = discord.Embed(title = "Plex Username", color= discord.Color.from_rgb(160,131,196))
    dmembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
    dmembed.add_field(name = '🤝', value='Please enter your  Plex username.', inline = True)
    dmembed.add_field(name = '⚠', value='Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).', inline = False)
    dmembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
    dmpassembed = discord.Embed(title = "Plex Password", color= discord.Color.from_rgb(160,131,196))
    dmpassembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
    dmpassembed.add_field(name = '🤝', value='Please enter your Plex password.', inline = True)
    dmpassembed.add_field(name = '⚠', value='Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).', inline = False)
    dmpassembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
    dmserverembed = discord.Embed(title = "Plex Servername", color= discord.Color.from_rgb(160,131,196))
    dmserverembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar_url)
    dmserverembed.add_field(name = '🤝', value='Please enter your Plex servername.', inline = True)
    dmserverembed.add_field(name = '⚠', value='Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2).', inline = False)
    dmserverembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
    await ctx.send(embed = messageembed)#tells user to link
    member = ctx.message.author
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
        await ctx.message.author.send('```Please be patient while I check your credentials. This will be a couple moments.```')
        try:
            account = MyPlexAccount(username, password)
            plex = account.resource(servername).connect()
            movies = plex.library.section('Movies')
            for video in movies.search(unwatched=True):
                print(video.title)
            await ctx.message.author.send('```Encrypted and saved your credentials. You are now able to host watch together sessions.```')
        except:
            await ctx.message.author.send('```❌ Your credentials are incorrect. Please try again. ❌```')
    except asyncio.TimeoutError:
        await ctx.message.author.send('```Timed out, please run >link again in the server.```')
        


client.run(CLIENTTOKEN)