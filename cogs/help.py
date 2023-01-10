import discord
from discord.ext import commands
from discord import Interaction
from discord import app_commands
import random

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Mostra o diálogo de ajuda.")
    async def help(self, interaction: Interaction):
        list = ["Agora 100% do comandos no /help!", "Agora com slash commands!", "Pessoas legais assistem filmes", "Utilizando Plex com um pouco de amor.", "Ajude a apoiar Mazi executando /donate!", "Agora mostrando, seus filmes!"]
        embed = discord.Embed(title = "Comandos disponíveis", colour = discord.Colour.from_rgb(229,160,13))
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
