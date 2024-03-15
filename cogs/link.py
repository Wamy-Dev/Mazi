import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Link(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="link", description="Vincule suas contas Plex e Discord.")
    async def link(self, interaction: Interaction):

        embed = discord.Embed(title = "Mazi Website", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
        embed.add_field(name = '🔗', value='https://mazi.pw/user', inline = False)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Link(client))
