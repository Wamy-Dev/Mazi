from discord.ext import commands
from discord import Interaction
from discord import app_commands

class Ping(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="ping", description="View the ping between Discord and Mazi.")
    async def donate(self, interaction: Interaction):

        txt = str(f"""```css\nIm not too slow right? {round(self.client.latency * 1000)}ms.```""")
        await interaction.response.send_message(txt)

async def setup(client):
    await client.add_cog(Ping(client))