import discord
import json
def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


async def send_close_dm(interaction, user):
    data = load_data()
    tickets = data.get("tickets", {})
    channel_id = str(interaction.channel.id)
    claim_id = data["claims"].get(channel_id, "Unclaimed")
    claim = interaction.guild.get_member(claim_id) if claim_id != "Unclaimed" else "Unclaimed"

    if channel_id not in tickets:
        return False 

    embed_dm = discord.Embed(
        title="Ticket Closed",
        description=f"Your ticket in **{interaction.guild.name}** has been closed. If you have any further questions, feel free to open a new ticket!",
        color=discord.Color.red()
    )

    embed_dm.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)

    embed_dm.add_field(name="Server", value=interaction.guild.name, inline=False)
    embed_dm.add_field(name="ID", value=f"#{interaction.channel.name}")
    embed_dm.add_field(name="Closed By", value=interaction.user.mention) 
    embed_dm.add_field(name="Claimed By", value=claim.mention if claim != "Unclaimed" else "Unclaimed")

    await user.send(embed=embed_dm)
    return True