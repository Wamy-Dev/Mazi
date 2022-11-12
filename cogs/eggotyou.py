import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Modal(discord.ui.Modal, title='You got me!'):
    feedback = discord.ui.TextInput(
        label='You found the Easter Egg!',
        style=discord.TextStyle.long,
        default='You found the Easter Egg! If you want your name in the source code, send a screenshot of this to Wamy#0002 and your name will be added.',
        required=False,
        max_length=135,
    )
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Thank you for using Mazi.', ephemeral=True)

class Eggotyou(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="egg", extras={"hidden": True})
    async def egg(self, interaction: Interaction):
        await interaction.response.send_modal(Modal())

async def setup(client):
    await client.add_cog(Eggotyou(client))