from socket import timeout
from plexapi.myplex import MyPlexAccount
import discord
from discord.ext import commands
from plexapi.server import PlexServer
from decouple import config
import asyncio
from argon2 import PasswordHasher
import sqlite3
import json
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('>'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
def login(discordid):
    query = cursor.execute(f"SELECT plexuser, plexpass, plexserver FROM creds WHERE discordid = {discordid}")
    data = cursor.fetchmany(1)
    username = data[0][0]
    hashedpassword = data[0][1]
    plexserver = data[0][2]
    #hashpassword
    ph.verify(hashedpassword, )
    return(username, hashedpassword, plexserver)


client = Bot()
CLIENTTOKEN = config('CLIENTTOKEN')
ph = PasswordHasher()
try: 
    connection = sqlite3.connect("creds.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE creds (discordid TEXT, plexuser TEXT, plexpass TEXT, plexserver TEXT)")
    print("Created new table.")
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
    embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
    embed.add_field(name = '>ping', value='Shows the ping between the bot and the user.', inline = False)
    embed.add_field(name = '>project', value='View the project github.', inline = False)
    embed.add_field(name = '>donate', value='Donate to the project.', inline = False)
    embed.add_field(name = '>counts', value='See how much media has been shared using this bot.', inline = False)
    embed.add_field(name = '>link', value='Link your Plex and Discord accounts to share with your friends. Not required unless you host the session.', inline = False)
    embed.add_field(name = '>unlink', value='Unlink your Plex and Discord accounts.', inline = False)
    embed.add_field(name = '>watch', value='Start a Plex Watch Togther session.', inline = False)
    await ctx.send(embed = embed)
######
@client.command(pass_context = True)
async def link(ctx):
    #checks if user is linked first
    discordid = ctx.message.author.id
    query = cursor.execute(f"SELECT * FROM creds WHERE discordid = {discordid}")
    if len(cursor.fetchall()) > 0:
        await ctx.send("```✔ Your account is already linked.```")
    else: 
        messageembed = discord.Embed(title = "Link your Plex and your Discord", color= discord.Color.from_rgb(160,131,196), description="🔗 Please check your pm's to link your accounts.")
        messageembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        messageembed.set_footer(text=f'This method is temporary and will be fixed in the future. Only send sensitive data to Mazi#2364. ♥')
        dmembed = discord.Embed(title = "🤝 Please enter your Plex username.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
        dmembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        dmembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        dmpassembed = discord.Embed(title = "🤝 Please enter your Plex password.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
        dmpassembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        dmpassembed.set_footer(text=f'This method is temporary and will be fixed in the future.')
        dmserverembed = discord.Embed(title = "🤝 Please enter your Plex servername.", color= discord.Color.from_rgb(160,131,196), description="⚠ Please read [here](https://github.com/Wamy-Dev/Mazi) about Mazi data safety. Your data is secure and encrypted with [Argon2id](https://en.wikipedia.org/wiki/Argon2). Only respond with your credentials if <@!978163786886311977> sent you this message, otherwise please ignore it.")
        dmserverembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
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
######
@client.command(pass_context = True)
async def unlink(ctx):
    discordid = ctx.message.author.id
    query = cursor.execute(f"SELECT * FROM creds WHERE discordid = {discordid}")
    if len(cursor.fetchall()) > 0:
        class Confirm(discord.ui.View):
            def __init__(self, ctx):
                super().__init__(timeout=30)
                self.value = None
                self.ctx = ctx
            @discord.ui.button(label='Confirm', style=discord.ButtonStyle.red)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.send_message('Deleting link.', ephemeral=True)
                cursor.execute(f"DELETE FROM creds WHERE discordid = {discordid}")
                connection.commit()
                await ctx.send("```🖐 Unlinked account. If you would like to relink in the future, run >link again.```")
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
########
@client.command(pass_context = True)
async def watch(ctx):
    discordid = ctx.message.author.id
    query = (f"SELECT * FROM creds WHERE discordid=?")
    result = cursor.execute(query, (discordid,))
    if len(cursor.fetchall()) > 0:
        class Selection(discord.ui.View):
            def __init__(self, ctx):
                super().__init__(timeout=30)
                self.value = None
                self.ctx = ctx
            @discord.ui.button(label='Movie', style=discord.ButtonStyle.green)
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                class MovieSelection(discord.ui.View):
                    def __init__(self, ctx):
                        super().__init__(timeout=30)
                        self.value = None
                        self.ctx = ctx
                    @discord.ui.button(label='Search for movie', style=discord.ButtonStyle.grey)
                    async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
                        await interaction.response.send_message("```Search```")
                        self.value = False
                        self.stop()
                    @discord.ui.button(label='Poll to decide', style=discord.ButtonStyle.red)
                    async def poll(self, interaction: discord.Interaction, button: discord.ui.Button):
                        await interaction.response.send_message("```Poll```")
                        self.value = False
                        self.stop()
                    @discord.ui.button(label='Let fate decide', style=discord.ButtonStyle.green)
                    async def random(self, interaction: discord.Interaction, button: discord.ui.Button):
                        await interaction.response.send_message("```Random```")
                        #logging in
                        if login(discordid):
                            print("logged in.")
                        else:
                            print("failed to login.")
                        self.value = False
                        self.stop()
                #
                movieembed = discord.Embed(title = "Movie Room Details", color= discord.Color.from_rgb(160,131,196), description="Please select a movie option.")
                movieembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                movieembed.add_field(name = 'Search', value='Allows you to search for a specific movie from your Plex movie library. Boring, but at least you know what you want.', inline = False)
                movieembed.add_field(name = 'Poll', value='Allows for a poll to decide the movie, which is in your Plex movie library. Allows the people to decide.', inline = False)
                movieembed.add_field(name = 'Random', value='Chooses a random movie from your Plex movie library. Makes the night a little more spicy.', inline = False)
                movieembed.set_footer(text=f'Please make a selection.')
                view = MovieSelection(ctx)
                await interaction.response.send_message(embed=movieembed, ephemeral=False, view=view)
                await view.wait()
                self.value = True
                self.stop()
            @discord.ui.button(label='TV Show', style=discord.ButtonStyle.blurple)
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                tvembed = discord.Embed(title = "Room Details", color= discord.Color.from_rgb(160,131,196), description="Please select a TV show option.")
                tvembed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
                tvembed.add_field(name = 'Show', value='Currently set to random from your Plex TV Show library.', inline = False)
                tvembed.add_field(name = 'Room Availability Time', value='Currently set at 10 minutes.', inline = False)
                tvembed.add_field(name = 'Spots', value='Currently set to 10 spots.', inline = False)
                tvembed.set_footer(text=f'Please make a selection.')
                await interaction.response.send_message(embed=tvembed, ephemeral=False)
                self.value = False
                self.stop()
            #
            async def on_timeout(self):
                await self.ctx.send("```❌ Timed out, did not finish creating room. Please run >watch again to create a room.```")
        embed = discord.Embed(title = "Room Details", color= discord.Color.from_rgb(160,131,196), description="Would you like to host a movie or a tv show room?")
        embed.set_author(name = ctx.message.author, icon_url = ctx.author.avatar.url)
        embed.set_footer(text=f'Please make a selection.')
        view = Selection(ctx)
        await ctx.send(embed=embed, view=view)
        await view.wait()
    else:
        await ctx.send("```❌ You do not have a linked account. If you would like to host a room, please run >link. Please also make sure your Plex server is powerful enough to host a room.```")
client.run(CLIENTTOKEN)