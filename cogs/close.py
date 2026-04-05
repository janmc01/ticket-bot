import discord
from discord.ext import commands, bridge
from discord.commands import slash_command, Option
import asyncio
import json

def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


class close(discord.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(closebutton())


    @bridge.bridge_command(name="close", description="Closes the current ticket")
    async def close(self, ctx):

        data = load_data(self)
        tickets = data["tickets"]

        #Check if the channel is a ticket channel
        if not str(ctx.channel.id) in tickets:
            return await ctx.respond("This command can only be used in a ticket channel.", ephemeral=True)


        embed = discord.Embed(
            title="Close Ticket",
            description=f"Do You Want To Close The Ticket? \n{ctx.author.mention}",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed, view=closebutton())
            

def setup(bot):
    bot.add_cog(close(bot))



class closebutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)



    @discord.ui.button(label="Close", 
                       style=discord.ButtonStyle.red, 
                       custom_id="close_button_command"
                       )
    async def close_callback_command(self, button, interaction):

        data = load_data(self)

        channel_id = str(interaction.channel.id)

        if channel_id in data["tickets"]:
            del data["tickets"][channel_id]

        if channel_id in data["claims"]:
            del data["claims"][channel_id]

        save_data(self, data)


        await interaction.response.send_message("The ticket will be closed in 5 seconds.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()
