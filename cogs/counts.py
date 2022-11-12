from discord.ext import commands
from discord import Interaction
from discord import app_commands
from firebase_admin import firestore

db = firestore.client()
countsdoc = db.collection(u'counts').document(u'counts')

class Counts(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    @app_commands.command(name="counts", description="View how many movie nights have been hosted globally.")
    async def donate(self, interaction: Interaction):
        counts = countsdoc.get()
        previouscount = counts.to_dict()
        txt = str(f"""```css\nThe bot has hosted movie night {str(previouscount["counts"] - 1)} times.```""")
        await interaction.response.send_message(txt)

async def setup(client):
    await client.add_cog(Counts(client))