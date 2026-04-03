import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import asyncio
import json

def load_data(self):
    with open("ticket_data.json", "r") as f:
        return json.load(f)

def save_data(self, data):
    with open("ticket_data.json", "w") as f:
        json.dump(data, f, indent=4)


class claim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="claim", description="Claim a ticket")
    async def claim(self, ctx):


        data = load_data(self)
        claims = data["claims"]
        tickets = data["tickets"]

        #Check if the channel is a ticket channel
        if not ctx.channel.id in tickets:
            return await ctx.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)


        #check for staff role
        staff_role = discord.utils.get(ctx.guild.roles, name="Discord Staff")
        if staff_role not in ctx.user.roles:
            return await ctx.response.send_message("You are not staff.", ephemeral=True)


        channel_id = str(ctx.channel.id)

        if channel_id in claims:            
            user = ctx.guild.get_member(claims[channel_id])
            if user == ctx.user:


                return await ctx.response.send_message(
                    f"{ctx.user.mention} you already claimed the ticket."
                )


            return await ctx.response.send_message(
                f"Ticket already claimed by {user.mention}",
                ephemeral=True
            )

        claims[channel_id] = ctx.user.id
        save_data(self, data)

        await ctx.channel.set_permissions(ctx.user, read_messages=True, send_messages=True)
        await ctx.channel.set_permissions(discord.utils.get(ctx.guild.roles, name="Discord Staff"), read_messages=True, send_messages=False)


        await ctx.response.send_message(
            f"Ticket claimed by {ctx.user.mention}"
        )

    @slash_command(name="unclaim", description="Unclaim a ticket")
    async def unclaim(self, ctx):


        data = load_data(self)
        claims = data["claims"]
        tickets = data["tickets"]


        #Check if the channel is a ticket channel
        if not ctx.channel.id in tickets:
            return await ctx.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)

        channel_id = str(ctx.channel.id)

        if channel_id in claims:            
            user = ctx.guild.get_member(claims[channel_id])
            if user == ctx.user:

                del claims[channel_id]
                save_data(self, data)

                await ctx.channel.set_permissions(discord.utils.get(ctx.guild.roles, name="Discord Staff"), read_messages=True, send_messages=True)
                await ctx.channel.set_permissions(ctx.user, read_messages=True, send_messages=False)

                return await ctx.response.send_message(
                    f"{ctx.user.mention} unclaimed the ticket."
                )




def setup(bot):
    bot.add_cog(claim(bot))