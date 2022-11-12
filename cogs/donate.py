import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Donate(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="donate", description="Doante to the Mazi project.")
    async def donate(self, interaction: Interaction):

        embed = discord.Embed(title = "Donate to the project", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
        embed.add_field(name = '🔗', value='https://homeonacloud.com/donate', inline = False)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Donate(client))