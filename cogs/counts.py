from discord.ext import commands
from discord import Interaction
from discord import app_commands
from firebase_admin import firestore

db = firestore.client()
countsdoc = db.collection(u'counts').document(u'counts')

class Counts(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="counts", description="Veja quantas sessões de pipoca foram realizadas globalmente.")
    async def donate(self, interaction: Interaction):
        counts = countsdoc.get()
        previouscount = counts.to_dict()
        txt = str(f"""```css\nO bot hospedou uma sessão pipoca {str(previouscount["counts"] - 1)} vezes.```""")
        await interaction.response.send_message(txt)

async def setup(client):
    await client.add_cog(Counts(client))
