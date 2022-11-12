import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands
import random

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Shows the help dialogue.")
    async def help(self, interaction: Interaction):
        list = ["Now with 100% more help!", "Now with slash commands!", "Cool cats watch movies.", "Runs on Plex and a little love.", "Help support Mazi by running /donate!", "Now showing, your movies!"]
        embed = discord.Embed(title = "Available commands", colour = discord.Colour.from_rgb(229,160,13))
        embed.set_author(name = interaction.user.display_name, icon_url = interaction.user.display_avatar.url)
        embed.set_footer(text = random.choice(list))
        try:
            for command in self.client.tree.get_commands():
                if command.extras.get("hidden"):
                    continue
                embed.add_field(name = f"</{command.name}:0>", value = command.description, inline = False)
        except Exception as e:
            print(e)
        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(Help(client))