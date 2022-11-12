import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Website(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="website", description="View the Mazi website.")
    async def website(self, interaction: Interaction):

        embed = discord.Embed(title = "Mazi Website", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
        embed.add_field(name = '🔗', value='https://mazi.pw', inline = False)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Website(client))