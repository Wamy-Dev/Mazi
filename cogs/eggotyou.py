import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Modal(discord.ui.Modal, title='You got me!'):
    feedback = discord.ui.TextInput(
        label='Você encontrou o Easter Egg!',
        style=discord.TextStyle.long,
        default='Você encontrou o Easter Egg! Se você quiser seu nome no código-fonte, envie uma captura de tela para Wamy#0002 e seu nome será adicionado.',
        required=False,
        max_length=135,
    )
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Obrigado por usar o Mazi.', ephemeral=True)

class Eggotyou(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="egg", extras={"hidden": True})
    async def egg(self, interaction: Interaction):
        await interaction.response.send_modal(Modal())

async def setup(client):
    await client.add_cog(Eggotyou(client))
