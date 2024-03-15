import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Project(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="project", description="Veja o repositório GitHub para Mazi.")
    async def project(self, interaction: Interaction):

        embed = discord.Embed(title = "Mazi Github", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
        embed.add_field(name = '🔗', value='https://github.com/Wamy-Dev/Mazi', inline = False)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Project(client))
