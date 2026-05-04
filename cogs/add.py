import discord
from discord.ext import commands, bridge
from discord.commands import slash_command, Option
import asyncio
import json
from discord.ext.bridge import BridgeOption

def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


class add(discord.Cog):
    def __init__(self, bot):
        self.bot = bot




    @bridge.bridge_command(name="add", description="add a user to the current ticket")
    async def add(self, ctx, user: BridgeOption(discord.User, "The user to add to the ticket")): # type: ignore

        data = load_data(self)
        tickets = data["tickets"]

        #Check if the channel is a ticket channel
        if not str(ctx.channel.id) in tickets:
            return await ctx.respond("This command can only be used in a ticket channel.", ephemeral=True)

        if user.id == ctx.author.id:
            return await ctx.respond("You cannot add yourself to the ticket.", ephemeral=True) 
        
        if user in ctx.channel.overwrites:
            return await ctx.respond("This user has already been explicitly added to this ticket.", ephemeral=True)
        
        await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
        await ctx.respond(f"{user.mention} has been added to the ticket by {ctx.author.mention}.", ephemeral=True)


    @bridge.bridge_command(name="remove", description="remove a user from the current ticket")
    async def remove(self, ctx, user: BridgeOption(discord.User, "The user to remove from the ticket")): # type: ignore

        data = load_data(self)
        tickets = data["tickets"]

        if not str(ctx.channel.id) in tickets:
            return await ctx.respond("This command can only be used in a ticket channel.", ephemeral=True)
        
        if user.id == ctx.author.id:
            return await ctx.respond("You cannot remove yourself from the ticket.", ephemeral=True) 
        
        if user not in ctx.channel.overwrites:
            return await ctx.respond("This user is not in the ticket.", ephemeral=True)
        
        if user.bot:
            return await ctx.respond("You cannot remove bots from the ticket via this command.", ephemeral=True)


        await ctx.channel.set_permissions(user, overwrite=None)
        await ctx.respond(f"{user.mention} has been removed from the ticket by {ctx.author.mention}.", ephemeral=True)

def setup(bot):
    bot.add_cog(add(bot))


