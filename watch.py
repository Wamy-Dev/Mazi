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