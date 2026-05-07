import discord
from discord.ext import commands, bridge
from discord.ext.bridge import BridgeOption
from discord.commands import slash_command, Option
import json
import datetime

def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


class blacklist(discord.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name="blacklist", description="Toggle a user's blacklist status for ticket creation.")
    async def blacklist(self, ctx, 
                  user: Option(discord.User, "The user to blacklist"),  # type: ignore
                  reason: Option(str, "The reason", required=False)): # type: ignore
        

        data = load_data(self)
        tickets = data["tickets"]
        blacklist = data["blacklist"]
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)

        if "blacklist" not in data:
            data["blacklist"] = {}
        if guild_id not in data["blacklist"]:
            data["blacklist"][guild_id] = {}

        staff_role = discord.utils.get(ctx.guild.roles, name="Discord Staff")
        if staff_role not in ctx.author.roles:
            return await ctx.respond("You are not staff.", ephemeral=True)

        
        if user_id in data["blacklist"][guild_id]:

            embed = discord.Embed(
                title="Please Confirm",
                color=discord.Color.orange()
            )

            await ctx.respond(embed=embed, view=blacklist_view(user=user, reason=reason), ephemeral=True)
        else:

            if user.id == ctx.author.id:
                return await ctx.respond("You cannot blacklist yourself.", ephemeral=True) 

            if user.bot:
                return await ctx.respond("You cannot blacklist bots.", ephemeral=True)
            
            data["blacklist"][guild_id][user_id] = {
                    "user_name": user.name,
                    "mod_id": ctx.author.id,
                    "mod_name": ctx.author.name,
                    "reason": reason or "No reason provided",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            save_data(self, data)

            embed = discord.Embed(
                title="Blacklist Update",
                description=f"**{user.name}** ({user.mention}) has been added to the blacklist by {ctx.author.mention}. \nReason: {reason or 'No reason provided'}",
                color=discord.Color.red()
            )

            try:

                dm_embed = discord.Embed(
                    title="Blacklist Notification",
                    description=f"You have been blacklisted from creating tickets in **{ctx.guild.name}**. Reason: {reason or 'No reason provided'}",
                    color=discord.Color.red()
                )
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                await ctx.send(f"Could not send DM to {user.mention}, but they have been blacklisted.", ephemeral=True)

            await ctx.respond(embed=embed, ephemeral=True)

class blacklist_view(discord.ui.View):
    def __init__(self, user, reason):
        super().__init__()
        self.user = user
        self.reason = reason


    @discord.ui.button(label="Remove from Blacklist", style=discord.ButtonStyle.green, custom_id="remove_from_blacklist")
    async def remove_from_blacklist(self, button: discord.ui.Button, interaction: discord.Interaction):
        data = load_data(self)
        guild_id = str(interaction.guild.id)
        user_id = str(self.user.id)

        if user_id in data["blacklist"][guild_id]:

            del data["blacklist"][guild_id][user_id]
            save_data(self, data)


            embed = discord.Embed(
                title="Blacklist Update",
                description=f"**{self.user.mention}** has been removed from the blacklist by {interaction.user.mention}.",
                color=discord.Color.green()
                
            )

            await interaction.response.edit_message(embed=embed, view=None)

            try:

                dm_embed = discord.Embed(
                    title="Blacklist Notification",
                    description=f"You have been removed from the blacklist in **{interaction.guild.name}**. Reason: {self.reason or 'No reason provided'}",
                    color=discord.Color.green()
                )
                await self.user.send(embed=dm_embed)
            except discord.Forbidden:
                await interaction.response.send_message(f"Could not send DM to {self.user.mention}, but they have been removed from the blacklist.", ephemeral=True)


            #await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("User is not in the blacklist.", ephemeral=True)
 



def setup(bot):
    bot.add_cog(blacklist(bot))


